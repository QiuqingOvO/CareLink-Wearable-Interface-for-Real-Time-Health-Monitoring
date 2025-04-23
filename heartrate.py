import asyncio
import json
import random
from aiohttp import web
from bleak import BleakScanner
import threading

# 全局变量存储最新心率
current_heart_rate = 0

async def index(request):
    """提供HTML页面"""
    try:
        with open('web/index.html', 'r') as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type='text/html')
    except FileNotFoundError:
        return web.Response(text="<html><body><h1>Heart Rate Monitor</h1></body></html>", 
                           content_type='text/html')

async def heartrate(request):
    """提供心率数据API"""
    global current_heart_rate
    # 设置CORS头，允许Flask应用访问
    return web.Response(text=str(current_heart_rate), 
                       headers={
                           'Access-Control-Allow-Origin': '*',
                           'Content-Type': 'text/plain'
                       })

async def setup_web_server():
    """设置并启动Web服务器"""
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/heartrate', heartrate)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # 尝试不同的端口，直到找到可用的
    ports = [3030, 3031, 3032, 3033, 3034]
    for port in ports:
        try:
            site = web.TCPSite(runner, '127.0.0.1', port)
            await site.start()
            print(f"心率服务器启动成功！监听地址: http://127.0.0.1:{port}")
            print(f"请确保Flask应用中的heartrate路由使用此URL: http://127.0.0.1:{port}/heartrate")
            
            # 修改Flask应用中的URL
            try:
                with open('main.py', 'r') as f:
                    content = f.read()
                
                if 'requests.get(\'http://127.0.0.1:3030/heartrate\')' in content:
                    new_content = content.replace(
                        'requests.get(\'http://127.0.0.1:3030/heartrate\')', 
                        f'requests.get(\'http://127.0.0.1:{port}/heartrate\')'
                    )
                    
                    with open('main.py', 'w') as f:
                        f.write(new_content)
                    
                    print(f"已自动更新Flask应用中的URL为: http://127.0.0.1:{port}/heartrate")
            except:
                print("无法自动更新Flask应用中的URL，请手动修改")
            
            break
        except OSError:
            print(f"端口 {port} 已被占用，尝试下一个...")
    else:
        print("所有端口都被占用，无法启动服务器")
        return
    
    # 保持服务器运行
    while True:
        await asyncio.sleep(3600)  # 1小时

async def scan_ble_devices():
    """扫描蓝牙设备获取心率数据"""
    global current_heart_rate
    try:
        print("开始扫描小米手环")
        while True:
            try:
                devices = await BleakScanner.discover()
                
                for device in devices:
                    # 处理设备广播数据
                    if device.metadata.get('manufacturer_data'):
                        for company_id, data in device.metadata['manufacturer_data'].items():
                            # 小米的公司ID是0x0157 (十进制为343)
                            if company_id == 343 and len(data) > 3:
                                heart_rate = data[3]
                                if heart_rate != 0xFF:  # 0xFF表示无效数据
                                    current_heart_rate = heart_rate
                                    print(f"{device.name} ({device.address}) Heart Rate: {heart_rate}")
            
            except Exception as e:
                print(f"扫描错误: {e}")
            
            # 短暂暂停后继续扫描
            await asyncio.sleep(1)
    
    except ImportError:
        print("未安装bleak库或蓝牙不可用")
        return
    
    #except ImportError:
        # 如果没有安装bleak库，使用模拟数据
        #print("未安装bleak库或蓝牙不可用，使用模拟心率数据")
        #while True:
            #current_heart_rate = random.randint(60, 100)
            #print(f"模拟心率: {current_heart_rate}")
            #await asyncio.sleep(1)

async def main():
    """主函数，同时运行蓝牙扫描和Web服务器"""
    # 创建两个任务并同时运行
    await asyncio.gather(
        scan_ble_devices(),
        setup_web_server()
    )

if __name__ == "__main__":
    # 在Windows上需要使用特定的事件循环策略
    if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("程序已停止")