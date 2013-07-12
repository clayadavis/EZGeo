EZGeo
=====

Okay, I dug up some old code. Attached is a zip file with some geocoding resources. It's not particularly well documented, but there's a geocoder_demo.py file in there that shows a couple examples. I know the API on bing has changed, but you should try the others (yahoo, google). You can use my API keys for testing, but if you're going above 500 queries a day or something, use a different key. They should be free if you want to get your own. I think some part of Truthy still uses my keys. Go ahead and try to use that code, see if any of it works for you.

Next is the blacklist code. People aren't very clever when coming up with pithy answers for their location. We can filter out a pretty large number of fake locations (e.g. Earth, on the dancefloor) with fuzzy string matching. The blacklist code has two parts, a python class and a textfile with the words to blacklist. Use it like so:

    import blacklist
    black_words = open("generated_blacklist.txt").read().split('\n')
    b = blacklist.Blacklist(black_words)

    tweet_location = <<some location string>>
    score, match = b.checkWord(tweet_location)
    if score > 0.7:
        <<it's junk>>
    else:
        <<go ahead and try to reverse-geocode it>>

The 0.7 is a heuristic, go ahead and adjust it if you'd like. Also, you're going to need to use another heuristic to split up combo place names like mine: "Austin, TX / Bloomington, IN". I would split those up on common dividers (/ | \ & and or) and look up the left half first, then the second half. Also, removing parenthetical expressions is useful, e.g. "Kirksville (hell), MO". The resolve_user_location_strings.py has these heuristics in it, along with some other useful stuff, but it's a total nightmare and is way undocumented.

If this all sounds like a bunch of totally random crap, it kinda is. But at the same time, I was going through millions of locations and these heuristics worked pretty well for me. I'm sorry about the state of this code; all I can say about that is that I promise I'm a better collaborator now than I was then :)
