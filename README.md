@HACK CAMBRIDGE ATLAS 2022

## Inspiration
On the 17th of December 2021, one month's worth of rain fell in a single day, flooding Malaysia and displacing tens of thousands of people. Despite our best efforts in slowing down the rate of climate change, we cannot deny that our planet is currently experiencing its effects.

Our aim was to create an automated flood helpline to aid the rescue efforts of Government organisations. During a flash flood, victims won't have time or bandwidth to download dedicated apps or navigate social media sites to seek help. We wanted a system that wouldn't gatekeep rescue to the technologically able.

## What it does

Victims are able to call in or text to report their situation, which is then relayed to a rescue coordinator. Our system visualises the locations of victims and clusters them into groups to which rescue boats can be dispatched.

## How we built it

We used the Twilio API to receive calls and text messages and Deepgram to convert the phone recordings into text. As the output is quite messy, we use GPT-3 to clean the transcribed address. Our backend was built on Python. We retrieved the geo data from geopy and created the visualisations with Plotly.

## Challenges we ran into

There were some issues mostly with hacking together different libraries that didn't do exactly what we wanted. Everything related to data input was tricky as address names are often mistyped, mispronounced and incorrectly detected by different engines - so we used advanced AI techniques like the GPT-3 model to correct them. For the server part we didn't have much experience so there were some hacks on how we process webpages. Designing a good path for the rescue isn't trivial as well, so we had to use some heuristics.

## Accomplishments that we're proud of

Imagine using the Twilio API and being greeted with a message inviting us to press any key to run our code... Then telling us there was an error. This was highly disappointing at first as we had made the mistake of celebrating too early, but in the marginally longer run, it just made our "Hello World" more rewarding.

## What we learned

For most of our team, our understanding of distributed systems was limited to the Further Java tick. During the 24 hours, we learned a lot about connecting APIs, hosting and producing a pipeline. 

## What's next for Flood Rescue Line

1. Better UI with more information about the spread of clusters and matching a database of dispatchable vehicles owned by the organisation to each cluster.
2. Adding path finding and deploy our system to mobile apps for navigators out on the water
3. Connecting our systems to drones which can deliver intermediate supplies for families who are predicted to experience delays in rescue - hence fully automating the provision of relief aid
