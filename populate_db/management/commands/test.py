str_name_full = 'SHIP N'

country_codes = {512: 'Solomon Islands', 617: 'Germany', 517: 'Tonga', 518: 'Tuvalu', 520: 'Vanuatu', 521: 'American Samoa (U.S.A.)', 522: 'Brunei', 523: 'Christmas Island (Australia)', 524: 'Cocos Islands (Australia)', 525: 'Cook Islands (New Zealand)', 526: 'Coral Sea Islands (Australia)', 527: 'Federated States Of Micronesia', 528: 'French Polynesia (France)', 529: 'Guam (U.S.A.)', 530: 'Johnston Atoll (U.S.A.)', 531: 'Marshall Islands', 532: 'New Caledonia (France)', 533: 'Niue (New Zealand)', 534: 'Norfolk Island (Australia)', 535: 'Northern Mariana Islands (U.S.A.)', 536: 'Belau', 537: 'Pitcairn Island (U.K.)', 538: 'Tokelau', 539: 'Wake Island (U.S.A.)', 540: 'Wallis And Futuna (France)', 541: 'Samoa', 624: 'Jordan', 632: 'Montenegro', 615: 'France', 648: 'Macedonia', 631: 'Moldova', 614: 'Finland', 650: 'Ukraine', 633: 'Netherlands', 616: 'Georgia', 601: 'Albania', 602: 'Armenia', 603: 'Austria', 604: 'Azerbaijan', 605: 'Belarus', 606: 'Belgium', 607: 'Bosnia And Herzegovina', 608: 'Bulgaria', 609: 'Croatia', 610: 'Cyprus', 611: 'Czech Republic', 612: 'Denmark', 101: 'Algeria', 102: 'Angola', 103: 'Benin', 104: 'Botswana', 105: 'Burkina Faso', 106: 'Burundi', 107: 'Cameroon', 108: 'Cape Verde', 109: 'Central African Republic', 110: 'Chad', 111: 'Comoros', 112: 'Congo', 113: "Cote D'Ivoire", 114: 'Djibouti', 115: 'Egypt', 116: 'Eritrea', 117: 'Ethiopia', 118: 'Gabon', 119: 'Ghana', 120: 'Guinea', 121: 'Guinea-Bissau', 122: 'Kenya', 123: 'Liberia', 124: 'Libya', 125: 'Madagascar', 126: 'Malawi', 127: 'Mali', 128: 'Mauritania', 129: 'Mauritius', 130: 'Morocco', 131: 'Mozambique', 132: 'Namibia', 133: 'Niger', 134: 'Nigeria', 647: 'Syria', 136: 'Sao Tome And Principe', 137: 'Senegal', 138: 'Seychelles', 139: 'Sierra Leone', 140: 'Somalia', 141: 'South Africa', 654: 'Madeira Islands (Portugal)', 143: 'Territory Of The French Southern And Antarctic Lands', 635: 'Poland', 147: 'British Overseas Territories', 148: 'Sudan', 149: 'Tanzania', 150: 'The Gambia', 151: 'Togo', 152: 'Tunisia', 153: 'Uganda', 154: 'Zaire', 155: 'Zambia', 156: 'Zimbabwe', 157: 'Amsterdam Island (France)', 158: 'Ascension Island (U.K.)', 159: 'Canary Islands (Spain)', 160: 'Ceuta (Spain)', 161: 'Chagos Archipelago (U.K.)', 162: 'Lesotho', 163: 'Mayotte (France)', 164: 'Melilla (Spain)', 165: 'Reunion Island (France)', 166: 'Rwanda', 167: 'Swaziland', 168: 'Tromelin Island (France)', 169: 'Western Sahara (Morocco)', 626: 'Latvia', 627: 'Lebanon', 628: 'Lithuania', 700: 'Antarctica', 701: 'Argentine Base In Antarctica', 629: 'Luxembourg', 620: 'Iceland', 630: 'Malta', 201: 'Afghanistan', 202: 'Bahrain', 203: 'Bangladesh', 204: 'Cambodia', 205: 'China', 206: "Democratic People'S Republic Of Korea", 207: 'India', 208: 'Iran', 209: 'Iraq', 210: 'Japan', 211: 'Kazakhstan', 212: 'Kuwait', 213: 'Kyrgyzstan', 214: 'Laos', 215: 'Mongolia', 216: 'Myanmar', 217: 'Nepal', 218: 'Oman', 219: 'Pakistan', 220: 'Qatar', 221: 'Republic Of Korea', 222: 'Russian Federation (Asian Sector)', 223: 'Saudi Arabia', 224: 'Sri Lanka', 227: 'Tajikistan', 228: 'Thailand', 229: 'Turkmenistan', 230: 'United Arab Emirates', 231: 'Uzbekistan', 232: 'Vietnam', 233: 'Yemen', 234: 'Macau (Portugal)', 235: 'Maldives', 236: 'Taiwan', 637: 'Romania', 638: 'Russian Federation (European Sector)', 639: 'Serbia', 622: 'Israel', 618: 'Greece', 641: 'Slovakia', 642: 'Slovenia', 643: 'Spain', 623: 'Italy', 645: 'Sweden', 800: 'Ship Stations', 646: 'Switzerland', 636: 'Portugal', 301: 'Argentina', 302: 'Bolivia', 303: 'Brazil', 304: 'Chile', 305: 'Colombia', 306: 'Ecuador', 307: 'Guyana', 308: 'Paraguay', 309: 'Peru', 649: 'Turkey', 312: 'Suriname', 313: 'Uruguay', 314: 'Venezuela', 315: 'French Guiana (France)', 316: 'Falkland Islands (U.K.)', 317: 'South Georgia (U.K.)', 651: 'United Kingdom', 652: 'Faroe Islands (Denmark)', 653: 'Gibraltar (U.K.)', 625: 'Kazakhstan', 401: 'Barbados', 402: 'Belize', 403: 'Canada', 405: 'Costa Rica', 406: 'Cuba', 407: 'Dominican Republic', 408: 'El Salvador', 409: 'Grenada', 410: 'Guatemala', 411: 'Haiti', 412: 'Honduras', 413: 'Jamaica', 414: 'Mexico', 415: 'Nicaragua', 416: 'Panama', 417: 'Saint Kitts And Nevis', 423: 'The Bahamas', 424: 'Trinidad And Tobago', 425: 'United States Of America', 426: 'Antigua And Barbuda', 427: 'Bermuda (U.K.)', 428: 'British Virgin Islands (U.K.)', 429: 'Cayman Islands (U.K.)', 430: 'Dominica', 431: 'Greenland (Denmark)', 432: 'Guadeloupe (France)', 433: 'Martinique (France)', 434: 'Netherlands Antilles (Netherlands)', 435: 'Puerto Rico (U.S.A.)', 436: 'Saint Lucia', 437: 'Saint Vincent And The Grenadines', 438: 'Saint Pierre & Miquelon Island (France)', 439: 'Turks And Caicos Islands', 440: 'Virgin Islands (U.S.A.)', 621: 'Ireland', 634: 'Norway', 613: 'Estonia', 619: 'Hungary', 501: 'Australia', 502: 'Fiji', 503: 'Indonesia', 504: 'Kiribati', 505: 'Malaysia', 506: 'Nauru', 507: 'New Zealand', 508: 'Papua New Guinea', 509: 'Philippines', 511: 'Singapore'}

print country_codes.get(102)

deliminator_idxs = [len(str_name_full)] # default deliminator: end of string

print deliminator_idxs

# find double whitespace '  '
if str_name_full.find('  ') > -1:
    deliminator_idxs.append(str_name_full.find('  '))

print deliminator_idxs

# find lonely opening parenthesis '('
if (str_name_full.find('(') > -1) and (str_name_full.find(')') == -1):
    deliminator_idxs.append(str_name_full.find('('))

print deliminator_idxs

# get the index of the first occurence of a deliminator
deliminator_idxs.sort()

print deliminator_idxs

print str_name_full[0:deliminator_idxs[0]].strip()
