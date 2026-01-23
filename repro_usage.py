from youtube_transcript_api import YouTubeTranscriptApi

try:
    video_id = 'w3jkJ2Sj78g' # Example from user
    ytt_api = YouTubeTranscriptApi()
    print("Fetching transcript...")
    transcript = ytt_api.fetch(video_id, languages=['ko'])
    
    print(f"Type of transcript: {type(transcript)}")
    print(f"Content of transcript: {transcript}")

    # Check if we can iterate and access it like a list of dicts
    if hasattr(transcript, '__iter__'):
        print("Transcript is iterable")
        try:
            first_item = list(transcript)[0]
            print(f"First item type: {type(first_item)}")
            print(f"First item: {first_item}")
        except IndexError:
            print("Transcript is empty")
    
except Exception as e:
    print(f"Error: {e}")
