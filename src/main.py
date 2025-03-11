import cv2
import time
import os
import json
import requests
from datetime import datetime

from web3 import Web3, HTTPProvider
from moviepy.video.io.VideoFileClip import VideoFileClip

def convert_avi_to_mp4(input_path, output_path):
    # Load the AVI video clip
    video_clip = VideoFileClip(input_path)

    # Export the video clip to MP4 format
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Close the video clip
    video_clip.close()

def connectWithBlockchain(acc):
    web3 = Web3(HTTPProvider('http://127.0.0.1:7545'))

    if acc == 0:
        web3.eth.defaultAccount = web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount = acc
    
    artifact_path = '../build/contracts/VideoFeed.json'
    with open(artifact_path) as f:
        artifact_json = json.load(f)
        contract_abi = artifact_json['abi']
        contract_address = artifact_json['networks']['5777']['address']
    
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)
    return contract, web3

def record_and_upload_video():
    # Set up OpenCV video capture
    capture = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_file = 'video.avi'
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    # Record video for 180 seconds
    start_time = time.time()
    while time.time() - start_time < 30: # 180 Seconds for 3 Minutes
        ret, frame = capture.read()
        if ret:
            out.write(frame)
        else:
            break

    # Release the video capture
    capture.release()
    out.release()
    output_file_path = "output_video.mp4"

    # Convert AVI to OGG
    convert_avi_to_mp4(output_file, output_file_path)

    # Upload the video to IPFS
    files = {'file': open('output_video.mp4', 'rb')}
    response = requests.post('http://127.0.0.1:5001/api/v0/add', files=files)
    print(response.json())  # Should return the CID (hash) of the uploaded file
    response=response.json()
    video_hash = response['Hash']
    print(video_hash)

    # Get current date and time
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Connect with blockchain and add video hash
    contract, web3 = connectWithBlockchain(0)
    print(date,time_str)
    tx_hash = contract.functions.addVideoHash(1, date, time_str, video_hash).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)

    # Delete the local video file
    os.remove(output_file)

def main():
    while True:
        record_and_upload_video()
        time.sleep(10)
        
if __name__ == "__main__":
    main()
