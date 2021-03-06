import asyncio
import json
from statistics import mean

from acolyte.constants import STATE_CHECK_STEPS, STATE_CHECK_TIMEOUT
from discord.ext.commands import Cog


class Brain(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message):
            await self.process_message(message)
        # Иначе закидываем сообщение на тренировку модели (кроме своих сообщений).
        else:
            text = message.content
            await self.bot.brain.post('http://brain:8080/train', data=text)

    async def process_message(self, message):
        if 'state' in message.content:
            await message.channel.send(
                'Не может быть, соизволил поинтересоваться моим самочувствием? '
                'Погоди, прощупаю свои чумные бубоны.'
            )
            states = []
            for step in range(STATE_CHECK_STEPS):
                response = await self.bot.brain.get('http://brain:8080/state')
                states.append(json.loads(await response.text()))
                await asyncio.sleep(STATE_CHECK_TIMEOUT)
            mean_cpu = mean(state['cpu'] for state in states)
            mean_ram = mean(state['mem'] for state in states)
            current_queue_size = states[-1]['queue_size']
            current_trained = states[-1]['trained']
            current_loss = states[-1]['last_epoch_loss']
            current_loss_std = states[-1]['loss_std']
            seconds_passed = STATE_CHECK_STEPS * STATE_CHECK_TIMEOUT
            messages_processed = states[0]['queue_size'] - current_queue_size
            processing_speed = messages_processed / seconds_passed
            output = (
                '```\n'
                + "\n".join(
                    [
                        f'\U0001F300 ЦПУ: {mean_cpu}%',
                        f'\U0001F4D5 Память: {mean_ram}%',
                        f'\U000026D3 В очереди: {current_queue_size}',
                        f'\U0001F4A8 Скорость обработки: {processing_speed}/с',
                        f'\U0001F552 Затренено эпох: {current_trained}',
                        f'\U0001F54C Лосс: {current_loss}',
                        f'\U0001F54D Отклонение лосса: {current_loss_std}',
                    ]
                )
                + '\n```'
            )
        else:
            response = await self.bot.brain.get('http://brain:8080/test')
            output = await response.text()
        await message.channel.send(output)


def setup(bot):
    bot.add_cog(Brain(bot))
