import discord
from discord import colour
from discord.ext import commands, tasks
import requests
import json
import os

from services.db_config import db
from Models.Item import Item
from Models.Order import Order

DIVINE_PRIDE_KEY = os.getenv('DIVINE_PRIDE_KEY')


class Tracker(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.notify.start()
        print(f'We are logged in as {self.client.user}')

    def fetch_items_by_id(self, id):
        baseUrl = f'https://www.novaragnarok.com/data/cache/ajax/item_{id}.json'
        response = requests.get(baseUrl)
        dPrideURL = f'https://www.divine-pride.net/api/database/Item/{id}?apiKey={DIVINE_PRIDE_KEY}'
        dPrideResponse = requests.get(dPrideURL)
        name = ''

        if dPrideResponse.status_code == 200:
            data = json.loads(dPrideResponse.text)
            name = data['name']
        else:
            name = 'Name Not Found'

        item = Item(id, name)

        if response.status_code == 200:
            json_data = json.loads(response.text)
            data = json_data['data']

            for i in data:
                price = 0
                location = ''
                qty = 1
                refine = 0

                if 'price' in i['orders']:
                    price = int(i['orders']['price'])
                if 'location' in i['orders']:
                    location = i['orders']['location'][:-1]
                if 'qty' in i['orders']:
                    qty = int(i['orders']['qty'])
                if 'refine' in i['orders']:
                    refine = int(i['orders']['refine'])

                order = Order(price, location, qty)
                item.orders.append(order)

            return item
        else:
            return None

    @tasks.loop(minutes=2)
    async def notify(self):
        full_track_list = db.tracker.find()

        for tracker in full_track_list:
            user = await self.client.fetch_user(tracker['user'])

            item = self.fetch_items_by_id(tracker['item'])
            item.orders.sort()
            prices = db.item.find_one({'_id': tracker['item']})

            if not prices or prices['min'] != item.orders[0].price or prices['max'] != item.orders[len(item.orders)-1].price:

                if not prices:
                    db.item.insert_one({
                        '_id': tracker['item'],
                        'min': item.orders[0].price,
                        'max': item.orders[len(item.orders)-1].price
                    })
                else:
                    db.item.update_one(
                        {'_id': tracker['item']},
                        {'$set': {'min': item.orders[0].price, 'max': item.orders[len(item.orders)-1].price}})

                embed = discord.Embed(
                    title=item.name,
                    url=f"https://www.novaragnarok.com/?module=vending&action=item&id={tracker['item']}",
                    color=discord.Colour.dark_green(),
                    description=f"> ** Item found on market with min price of `{item.orders[0].price:,}z` **"
                )
                embed.set_thumbnail(
                    url=f"https://www.divine-pride.net/img/items/item/iRO/{tracker['item']}")
                await user.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! `{round(self.client.latency * 1000)}ms`')

    @commands.command()
    async def test(self, ctx, id):
        item = self.fetch_items_by_id(id)

        price_column = ''
        location_column = ''
        qty_column = ''

        if item is not None:
            item.orders.sort()
            for order in item.orders:
                price_column += f'\n> {order.price:,}z'
                location_column += f'\n> {order.location}'
                qty_column += f'\n> {order.qty}'

            embed = discord.Embed(
                title=item.name,
                url=f'https://www.novaragnarok.com/?module=vending&action=item&id={id}',
                color=discord.Colour.dark_green()
            )
            embed.set_thumbnail(
                url=f'https://www.divine-pride.net/img/items/item/iRO/{id}')
            embed.add_field(
                name=f'** Price **', value=f'{price_column}', inline=True)
            embed.add_field(
                name=f'** Location **', value=f'{location_column}', inline=True)
            embed.add_field(
                name=f'** Quantity **', value=f'{qty_column}', inline=True)
            await ctx.send(embed=embed)

    @commands.command()
    async def track(self, ctx, id: int, refine=None):
        ref = 0
        if refine is not None:
            ref = int(refine.split('=')[1])

        if id:
            item = self.fetch_items_by_id(id)
            if item is not None:
                if db.tracker.find_one({'user': ctx.author.id, 'item': int(id)}):
                    await ctx.send(f'{ctx.author.mention} this item is already being tracked by you!')
                else:
                    tracker = {
                        'item': int(id),
                        'user': ctx.author.id,
                        'refine': refine
                    }
                    db.tracker.insert_one(tracker)
                    await ctx.send(f'{ctx.author.mention} you are now tracking {id}')
            else:
                await ctx.send(f'Hey human, I think this item does not exist')
        else:
            await ctx.send(f'{ctx.author.mention} expected a number as id for `${ctx.command}`')

    @commands.command()
    async def untrack(self, ctx, id):
        if id.isdigit():
            if db.tracker.find_one({'user': ctx.author.id, 'item': int(id)}):
                db.tracker.remove({'user': ctx.author.id, 'item': int(id)})
                item = self.fetch_items_by_id(id)

                embed = discord.Embed(colour=discord.Colour.dark_red())
                embed.add_field(name='`$Untrack`',
                                value=f"Item [{item.id}] {item.name} removed from your track list!")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(colour=discord.Colour.dark_red())
                embed.add_field(name='`$Untrack`',
                                value=f"Item not in your track list. Nothing was done!")
                await ctx.send(embed=embed)

    @commands.command()
    async def showtrack(self, ctx):
        items = db.tracker.find({'user': ctx.author.id})
        for item in items:
            print(item)


def setup(client):
    client.add_cog(Tracker(client))
