# HCFI
Interface for interacting with the HCFactions website - a web scraper

**Requirements**

* Python 3.X
* BeautifulSoup 4
* Arrow

**Getting Started**

First you'll need to import the module:

    import hcfi

Then you'll need to create your interface object:

    hcf = hcfi.HCFI()

From there you can get player/faction data like so:

    player = hcf.getPlayer('TeaEarlGray')
    kills = player.data['Kills']
  
    print('A true PvP master, ' + str(kills) + ' kills!')
  
Possible keys for the data dict are shown in the Regex patters that parse the <li> elements' text.

Get Legendary's faction, and request all of it's member's data, one at a time

    fac = hcf.getFaction('Legendary', True)

**Notes**

* Factions and Player pages are cached for 60s
* Any dates are automatically converted to arrow objects.
* US/Central timezone is hard-coded in (I believe that's the time zone everything operates within on HCF)
