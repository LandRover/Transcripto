# Transcripto
Install dependencies:

$ pip install -r requirements.txt

$ export OPENAI_API_KEY="your_api_key_here"
$ python main.py "http://example.com/audio.mp3" --output my_output.txt --summarize


# generate output
# I have this project, can you format it nicely here so we can start discussing it?
find . -type f -name "*.py" -exec sh -c 'echo "--- File: {} ---" >> ./project_content.txt; cat {} >> ./project_content.txt; echo -e "\n" >> ./project_content.txt' \;
