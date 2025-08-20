import discord
from discord.ext import tasks, commands
from ultralytics import YOLO
from picamera2 import Picamera2, Preview
import time

userID = ''
botToken= ''

model = YOLO("yolo11s.pt")
picam2 = Picamera2()
still_config = picam2.create_still_configuration(main={"size": (1920, 1080)})
video_config = picam2.create_video_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")

picam2.configure(still_config)
picam2.start()
time.sleep(2)

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')

    user = await client.fetch_user(userID)
    await user.send('👀')

    if not checkForCat.is_running():
        checkForCat.start()

@tasks.loop(seconds=5.0)
async def checkForCat(conf_threshold=0.25):
    user = await client.fetch_user(userID)
    picam2.stop()
    picam2.configure(still_config)
    picam2.start()
    picam2.capture_file("luna.jpg")

    results = model('luna.jpg', conf=conf_threshold)

    names  = model.names
    boxes  = results[0].boxes
    labels = [names[int(cls)] for cls in boxes.cls]

    if "cat" in labels:
        await user.send("Meow! I am eating")
        await user.send(file=discord.File('luna.jpg'))
        checkForCat.change_interval(seconds=300)
        print('Cat detected, waiting 5 mins.')
        picam2.stop()
        picam2.configure(video_config)
        picam2.start()
        picam2.start_and_record_video("luna.mp4", duration=10)
        time.sleep(15)
        await user.send(file=discord.File('luna.mp4'))

    else:
        checkForCat.change_interval(seconds=5.0)

client.run(botToken)
