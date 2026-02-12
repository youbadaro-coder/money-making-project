from dotenv import load_dotenv
import os
import sys

print("Start env test", flush=True)
load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print(f"Key found: {bool(key)}", flush=True)
if key:
    print(f"Key length: {len(key)}", flush=True)
print("End env test", flush=True)
