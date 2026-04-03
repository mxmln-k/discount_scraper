PERIOD_NOT_VERIFIED = "Angebotsdauer konnte nicht verifiziert werden!"

__BASE_HTML_TEMPLATE__ = """
<html>
    <body>
        <h1>Angebote der kommenden Woche</h1>
        
        {stores}
    </body>
</html>
"""

__FAILED_HTML_TEMPLATE__ = """
<hr>

<h3>{name}</h3>

<i>Parsen ist fehlgeschlagen!</i>
"""

__STORE_HTML_TEMPLATE__ = """
<hr>

<h3>{name}</h3>
<ul>
    {categories}
</ul>
"""

__CATEGORY_HTML_TEMPLATE__ = """
<li>
    <h4>{name}</h4>
    <ol>
        {offers}
    </ol>
</li>
"""

__OFFER_HTML_TEMPLATE__ = """
<li>
    <b>{name}</b>
    <!-- <img src="https://via.placeholder.com" alt="Description of Image" width="150"> -->
    <ul>
        {infos}
    </ul>
</li>
"""

__INFO_HTML_TEMPLATE__ = """
<li>{content}</li>
"""

__BASE_PLAIN_TEMPLATE__ = """
Angebote der kommenden Woche
        
{stores}
"""

__FAILED_PLAIN_TEMPLATE__ = """
 ----------------------------------------

 {name}
 Parsen ist fehlgeschlagen!

"""

__STORE_PLAIN_TEMPLATE__ = """
 ----------------------------------------

 {name}
 {categories}

"""

__CATEGORY_PLAIN_TEMPLATE__ = """
    {name}
    {offers}
"""

__OFFER_PLAIN_TEMPLATE__ = """
        - {name}
          {infos}
"""

__INFO_PLAIN_TEMPLATE__ = """
            {content}
"""

TEMPLATES = {
    "plain": {
        "base": __BASE_PLAIN_TEMPLATE__,
        "store": __STORE_PLAIN_TEMPLATE__,
        "category": __CATEGORY_PLAIN_TEMPLATE__,
        "offer": __OFFER_PLAIN_TEMPLATE__,
        "info": __INFO_PLAIN_TEMPLATE__,
        "failed": __FAILED_PLAIN_TEMPLATE__,
    },
    "html": {
        "base": __BASE_HTML_TEMPLATE__,
        "store": __STORE_HTML_TEMPLATE__,
        "category": __CATEGORY_HTML_TEMPLATE__,
        "offer": __OFFER_HTML_TEMPLATE__,
        "info": __INFO_HTML_TEMPLATE__,
        "failed": __FAILED_HTML_TEMPLATE__,
    },
}
