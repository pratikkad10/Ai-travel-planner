Project: AI Travel Budget Planner

"I'm going to Japan for 7 days. My hotel costs ¥12,000 per night, food costs ¥4,000 per day, and transportation will cost ¥2,000 per day. My home currency is INR. Calculate my total budget."

1. What information does the application need?
Destination
Number of days
Home currency
Hotel cost
Food cost
Transportation cost
Activities cost
Flight cost

Step 2 — Define the output

Suppose the user says:

I'm going to Japan for 7 days.

What should your application eventually return?

Think like a backend developer.

Would you want something like:

Flight
Hotel
Food
Transportation
Activities
Miscellaneous
----------------
Total

Important question

Would you return:

₹125,000

or something structured like:

{
    "flight": ...,
    "hotel": ...,
    "food": ...,
    "transport": ...,
    "activities": ...,
    "total": ...
}