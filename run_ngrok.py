import os
import time
import subprocess
import requests

def get_ngrok_url(max_attempts=10, delay=20):
    print("Attempting to get ngrok URL...")
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Waiting {delay} seconds for ngrok to start, attempt {attempt}/{max_attempts}")
            time.sleep(delay)
            print("Sending request to ngrok API...")
            response = requests.get("http://localhost:4040/api/tunnels", timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"Ngrok API response: {data}")
            for tunnel in data["tunnels"]:
                if tunnel["proto"] == "https":
                    url = tunnel["public_url"]
                    print(f"Got ngrok URL: {url}")
                    return url
            print(f"No HTTPS tunnel found, attempt {attempt}/{max_attempts}")
        except Exception as e:
            print(f"Error getting ngrok URL, attempt {attempt}/{max_attempts}: {e}")
        time.sleep(delay)
    raise Exception("Failed to get ngrok URL after maximum attempts")

def main():
    print("Starting ngrok...")
    print(f"NGROK_AUTH_TOKEN: {os.getenv('NGROK_AUTH_TOKEN')[:10]}...")  # Частично скрываем токен
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", "80", "--authtoken", os.getenv("NGROK_AUTH_TOKEN")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        url = get_ngrok_url()
        print(f"Writing URL to file: {url}")
        with open("/ngrok_data/ngrok_url.txt", "w") as f:
            f.write(url)
        print("URL written to /ngrok_data/ngrok_url.txt")
        os.chmod("/ngrok_data/ngrok_url.txt", 0o666)
        print("Set permissions to 666 for ngrok_url.txt")
        ngrok_process.wait()
    except Exception as e:
        print(f"Error: {e}")
        ngrok_process.terminate()
        stdout, stderr = ngrok_process.communicate()
        print(f"Ngrok stdout: {stdout.decode()}")
        print(f"Ngrok stderr: {stderr.decode()}")
        raise
    finally:
        ngrok_process.terminate()

if __name__ == "__main__":
    main()
