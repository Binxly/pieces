#
# pieces - An experimental BitTorrent client
#
# Copyright 2016 markus.eliasson@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import asyncio
import signal
import logging
from concurrent.futures import CancelledError
from pieces.torrent import Torrent
from pieces.client import TorrentClient

async def async_main(args):
    client = TorrentClient(Torrent(args.torrent))
    
    # Setup signal handling
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    
    def signal_handler():
        logging.info('Exiting, please wait until everything is shutdown...')
        client.stop()
        if not stop.done():
            stop.set_result(None)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await asyncio.gather(
            client.start(),
            stop
        )
    except CancelledError:
        logging.warning('Event loop was canceled')
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('torrent', help='the .torrent to download')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='enable verbose output')

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        pass
