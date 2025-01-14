import asyncio
import os

loop = asyncio.new_event_loop()


async def ping(ip: str):
    return os.system(f'ping -c 1 -q {ip} 2>&1 > /dev/null')


async def collect_hosts(iface: str, loop):
    ip, netmask = iface.split('/')
    byte1, byte2, byte3, byte4 = [int(i) for i in  ip.split('.')]
    num_ips = 2 ** (32 - int(netmask))
    print(f'Starting ping scan starting from ip {ip} for {num_ips} hosts.')

    ips = [ip]
    for _ in range(num_ips):
        byte4 +=1
        if byte4 > 255:
            byte4 = 0
            byte3 += 1
        if byte3 > 255:
            byte3 = 0
            byte2 += 1
        if byte2 > 255:
            byte2 = 0
            byte1 += 1
        ips.append(f'{byte1}.{byte2}.{byte3}.{byte4}')
    print(f'Last ip to scan is {ips[-1]}')

    hosts = []

    for ip in ips:
        async def helper():
            print(f'starting {ip}')
            if await ping(ip) == 0:
                print(f'host {ip} is up!')
                hosts.append(ip)

        loop.create_task(helper())
    await asyncio.sleep(0)

    tasks = asyncio.all_tasks(loop)
    tasks.remove(asyncio.current_task(loop))
    await asyncio.wait(tasks)




asyncio.run(collect_hosts('192.168.178.0/24', loop))
