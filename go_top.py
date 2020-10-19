import os
import uuid
import signal
import asyncio
import subprocess


class GoTop(object):

    def __init__(self):
        self.flag_keep_running = True
        self.WAIT_FOR = int(os.environ.get('WAIT_FOR'))

    def signal_handler(self, *args, **kwargs):
        self.flag_keep_running = False
        asyncio.create_task(self.take_a_break())

    @staticmethod
    async def take_a_break():
        for t in asyncio.all_tasks():
            t.cancel()
        asyncio.get_event_loop().stop()

    async def lets_go(self):
        while self.flag_keep_running:
            new_secret = uuid.uuid4().hex
            with open('secret', 'w') as f:
                f.write(new_secret)

            result = subprocess.call(['git', 'commit', '-am', new_secret])
            if result == os.EX_OK:
                _ = subprocess.call(['git', 'push', 'origin', 'master'])
            else:
                print(":'(")

            counter = 1
            while not counter % self.WAIT_FOR == 0:
                await asyncio.sleep(1)
                counter = counter + 1


if __name__ == '__main__':
    go_top = GoTop()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, go_top.signal_handler)
    loop.add_signal_handler(signal.SIGINT, go_top.signal_handler)
    loop.create_task(go_top.lets_go())
    loop.run_forever()
