import time
from dotenv import load_dotenv  # load environment variables from .env file
load_dotenv()
from openai import OpenAI
client = OpenAI()

def create_outfit(style):
    print(style)

    clothes=""
    for part in style:
        total=""
        for tag in part.tags:
            total +=tag
        item = f" A {part.type} in {part.color} with a style for {part.tags} \n"
        clothes += "- " + item 

    prompt=f"""
    I want you to create an image of a model wearing a specfici outfit.
    The outfit is for a {style[0].gender}
    The outfit will consist of:
    {clothes}
    *Important: Show just the human in the photo and also do not show the head
    """
    start_time=time.time()
    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    print(result.data[0].url)
    print(f"Time taken: {time.time()-start_time}")

    return result