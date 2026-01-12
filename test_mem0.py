from mem0 import MemoryClient
import os
import json
from dotenv import load_dotenv
import logging

load_dotenv()

user_name = "Aman"
mem0 = MemoryClient()

def add_memory():

    message_formatted = [
        {"role": "user",
         "content": "I really like The Weekend's music."},

         {"role": "assistant",
          "content": "Oh, that's cool! The Weekend has some great songs."},

          {"role": "user",
           "content": "Yeah, I so too"},

           {"role": "assistant",
            "content": "What's your favorite song by The Weekend?"},

    ]
    mem0.add(message_formatted, user_id=user_name)

def get_memory_by_query():
    mem0 = MemoryClient()
    query = "What are {user_name}'s preferences?"
    results = mem0.search(query, user_id=user_name)

    memories = [
            {
                "memory": result["memory"],
                "updated_at": result["updated_at"]
            }
            for result in results
        ]
    memories_str = json.dumps(memories)
    print(f"Memories: {memories_str}")
    return memories_str


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    get_memory_by_query()