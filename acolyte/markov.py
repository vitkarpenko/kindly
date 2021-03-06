import os
import random
from pathlib import Path

import discord
import markovify
from discord.ext import commands


class Markov(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = (
            Path(os.path.dirname(os.path.abspath(__file__))).parent / "data"
        )
        self.text_paths = [
            "mim.txt",
            "fallout.txt",
            "parsDeva.txt",
            "parsKandid.txt",
            "parsMonach.txt",
            "kamu.txt",
            "evrika.txt",
            "gosud.txt",
            "monten.txt",
            "evrika.txt",
            "sharpe.txt",
            "horn.txt",
            "komm.txt",
            "larosh.txt",
            "eterna.txt",
        ]

        models = []
        for text_path in self.text_paths:
            with open(self.data_folder / text_path) as text:
                models.append(markovify.NewlineText(text, state_size=3))
        weights = [43, 80, 33, 15, 80, 25, 6.7, 4, 8, 33, 2, 2.3, 15, 117, 1]
        self.model = markovify.combine(models, weights)

    async def on_message(self, message):
        if self.bot.user.mentioned_in(message):
            phrase = self.model.make_short_sentence(250)
            while not phrase:
                phrase = self.model.make_short_sentence(250)
            phrase = phrase[0].lower() + phrase[1:]
            await self.bot.send_message(
                message.channel, f"{message.author.mention}, {phrase}"
            )


def setup(bot):
    bot.add_cog(Markov(bot))
