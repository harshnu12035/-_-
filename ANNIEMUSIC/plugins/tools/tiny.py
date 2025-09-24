import os
import cv2
from PIL import Image
from pyrogram import filters
from ANNIEMUSIC import app


@app.on_message(filters.command("tiny") & filters.reply)
async def tiny_sticker(client, message):
    reply = message.reply_to_message
    if not reply or not reply.sticker:
        return await message.reply("Please reply to a sticker!")

    status = await message.reply("Processing... 🐾")

    try:
        # Download sticker
        file_path = await client.download_media(reply)

        # Background image
        bg = Image.open("ANNIEMUSIC/assets/rajnish.png")

        # Handle .tgs (Lottie Stickers)
        if file_path.endswith(".tgs"):
            os.system(f"lottie_convert.py {file_path} json.json")
            with open("json.json", "r") as f:
                jsn = f.read().replace("512", "2000")
            with open("json.json", "w") as f:
                f.write(jsn)
            os.system("lottie_convert.py json.json fixed.tgs")
            out_file = "fixed.tgs"
            os.remove("json.json")

        # Handle GIF/MP4 animated stickers
        elif file_path.endswith((".gif", ".mp4")):
            cap = cv2.VideoCapture(file_path)
            success, frame = cap.read()
            cap.release()
            if not success:
                return await status.edit("Error reading video frame!")

            cv2.imwrite("frame.png", frame)
            im = Image.open("frame.png")

            # Resize proportionally
            im_resized = im.resize((200, 200))
            im_resized.save("sticker.png")

            # Paste onto background
            bg_copy = bg.copy()
            bg_copy.paste(im_resized, (150, 0))
            bg_copy.save("output.webp", "WEBP", quality=95)
            out_file = "output.webp"

            os.remove("frame.png")
            os.remove("sticker.png")

        # Handle normal PNG/WEBP stickers
        else:
            im = Image.open(file_path)

            im_resized = im.resize((200, 200))
            im_resized.save("sticker.png")

            bg_copy = bg.copy()
            bg_copy.paste(im_resized, (150, 0))
            bg_copy.save("output.webp", "WEBP", quality=95)
            out_file = "output.webp"

            os.remove("sticker.png")

        # Send file
        await client.send_document(
            message.chat.id,
            out_file,
            reply_to_message_id=message.id
        )

    except Exception as e:
        await status.edit(f"Error: {e}")
        return

    finally:
        await status.delete()
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(out_file):
            os.remove(out_file)