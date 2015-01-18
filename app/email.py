# email.py
# This file contains all methods related to sending emails using flask-mail.
from flask import request

from flask.ext.mail import Message
from app import app, mail
from app.models import Profile, Listing


app.config["MAIL_SERVER"] = "localhost"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "roommatefinder@kevinlin.info"
app.config["MAIL_PASSWORD"] = "riceapps"


@app.route('/notification_email')
def notification_email():
    joiner_netid = request.args.get("joiner", None)
    poster_netid = request.args.get("poster", None)
    listing_id = request.args.get("listing", None)
    interest_notification(joiner_netid, poster_netid, listing_id)
    return "success"


def welcome_email(net_id):
    """
    Welcome email sent to the user after he/she first creates an account.

    Parameters:
    net_id: Net ID of the recipient
    recipient: Email address of the recipient
    """
    user = Profile.query.filter_by(net_id=net_id).first()
    msg = Message("Welcome to Roommate Finder.", sender=("Rice Roommate Finder", "roommatefinder@rice.edu"))
    msg.add_recipient((user.name, "" + net_id + "@rice.edu"))
    msg.html = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" ng-app="roommateFinder">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

        <!--Fonts-->
        <link href='http://fonts.googleapis.com/css?family=Oxygen:400,300,700' rel='stylesheet' type='text/css'>
        <link href='http://fonts.googleapis.com/css?family=Oswald:400,300,700' rel='stylesheet' type='text/css'>

        <style type="text/css">
            * {
                margin: 0;
                padding: 0;
            }
            body {
                background-color: #1F2021;
            }
            p.heading {
                font-family: 'Oxygen', sans-serif;
                font-weight: 700;
                letter-spacing: 1px;
                font-size: 26px;
                color: #E0E0E0;
            }
            p.subheading {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 20px;
                color: #E0E0E0;
            }
            p.text {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 16px;
                color: #E0E0E0;
            }
            p.footer {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 10px;
                color: #B3B3B3;
            }
            .link a:link {
                color: #409AB3;
                text-decoration: none;
            }
            .link a:hover {
                color: #409AB3;
                text-decoration: none;
                border-bottom: 2px solid #409AB3;
            }
            .link a:visited {
                color: #409AB3;
                text-decoration: none;
                }
            .link a:active {
                color: #409AB3;
                text-decoration: none;
            }
            .footerlink a:link {
                color: #B3B3B3;
                text-decoration: none;
            }
            .footerlink a:hover {
                color: #B3B3B3;
                text-decoration: none;
                border-bottom: 1px solid #B3B3B3;
            }
            .footerlink a:visited {
                color: #B3B3B3;
                text-decoration: none;
            }
            .footerlink a:active {
                color: #B3B3B3;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <td width="20%"></td>
                <td width="60%">
                    <br/><br/>
                    <img src="http://roommatefinder.riceapps.org/static/graphics/logo_email.png" width="375px" height="75px" style="height: 75px; width: 375px;" />
                    <br/><br/><br/>
                    <p class="heading">Hey """ + user.name.split(" ")[0] + """.</p>
                    <p class="subheading">Welcome to Roommate Finder.</p>
                    <br/><br/>
                    <p class="text">Roommate Finder is designed to ease the process of finding off campus roommates. Thanks for joining, and we hope you find it useful.</p>
                    <br/>
                    <div class="link">
                        <p class="text">Here are some helpful links to help you get started:</p>
                        <p class="text"><a href="http://roommatefinder.riceapps.org/search">Browse posted listings</a> - Look at listings that others have already posted on Roommate Finder.</p>
                        <p class="text"><a href="http://roommatefinder.riceapps.org/create_listing">Post a listing</a> - Have an apartment or planning to rent one? Create a Craigslist-style listing to see if others want to join you.</p>
                        <p class="text"><a href="http://roommatefinder.riceapps.org/users">Browse other users</a> - See other users of Roommate Finder, and possibly get in touch with someone you think you'd like to share an apartment with.</p>
                        <p class="text"><a href="http://roommatefinder.riceapps.org/my_profile">Edit your profile</a> - Link your Facebook account or add/edit your profile information. We encourage you to be as detailed as you can!</p>
                        <br/>
                        <p class="text">Don't hesistate to <a href="mailto:kevinlin@rice.edu">email us</a> if you have any questions.</p>
                    </div>
                    <br/><br/>
                    <p class="text">Sincerely,</p>
                    <p class="text">The Roommate Finder team, Rice Apps</p>
                    <br/><br/><br/>
                    <p class="footer">ROOMMATE FINDER, A PROJECT OF RICE APPS, 2015</p>
                    <div class="footerlink">
                        <p class="footer"><a href="http://roommatefinder.riceapps.org/about">ABOUT</a> | <a href="http://roommatefinder.riceapps.org/privacy_policy">PRIVACY POLICY</a> | <a href="mailto:kevinlin@rice.edu">CONTACT</a></p>
                    </div>
                    <br/><br/><br/><br/><br/>
                </td>
                <td width="20%"></td>
            </tr>
        </table>
    </body>
</html>
    """
    mail.send(msg)


def interest_notification(joiner_netid, poster_netid, listing_id):
    """
    Sends poster_netid a notification that joiner_netid is interested in the listing identified by listing_id.
    """
    joiner = Profile.query.filter_by(net_id=joiner_netid).first()
    poster = Profile.query.filter_by(net_id=poster_netid).first()
    listing = Listing.query.filter_by(id=listing_id).first()

    # Message sent to poster
    poster_msg = Message("Roommate Finder - Someone is interested!", sender=("Rice Roommate Finder", "roommatefinder@rice.edu"), reply_to="" + joiner_netid + "@rice.edu")
    poster_msg.add_recipient((poster.name, "" + poster_netid + "@rice.edu"))
    poster_msg.html = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" ng-app="roommateFinder">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

        <!--Fonts-->
        <link href='http://fonts.googleapis.com/css?family=Oxygen:400,300,700' rel='stylesheet' type='text/css'>
        <link href='http://fonts.googleapis.com/css?family=Oswald:400,300,700' rel='stylesheet' type='text/css'>

        <style type="text/css">
            * {
                margin: 0;
                padding: 0;
            }
            body {
                background-color: #1F2021;
            }
            p.heading {
                font-family: 'Oxygen', sans-serif;
                font-weight: 700;
                letter-spacing: 1px;
                font-size: 26px;
                color: #E0E0E0;
            }
            p.subheading {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 20px;
                color: #E0E0E0;
            }
            p.text {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 16px;
                color: #E0E0E0;
            }
            p.footer {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 10px;
                color: #B3B3B3;
            }
            .link a:link {
				color: #409AB3;
				text-decoration: none;
			}
			.link a:hover {
				color: #409AB3;
				text-decoration: none;
				border-bottom: 2px solid #409AB3;
			}
			.link a:visited {
				color: #409AB3;
				text-decoration: none;
			}
			.link a:active {
				color: #409AB3;
				text-decoration: none;
			}
            .footerlink a:link {
				color: #B3B3B3;
				text-decoration: none;
			}
			.footerlink a:hover {
				color: #B3B3B3;
				text-decoration: none;
				border-bottom: 1px solid #B3B3B3;
			}
			.footerlink a:visited {
				color: #B3B3B3;
				text-decoration: none;
			}
			.footerlink a:active {
				color: #B3B3B3;
				text-decoration: none;
			}
        </style>
    </head>
    <body>
        <table>
            <tr>
                <td width="20%"></td>
                <td width="60%">
                    <br/><br/>
                    <img src="http://roommatefinder.riceapps.org/static/graphics/logo_email.png" width="375px" height="75px" style="height: 75px; width: 375px;" />
                    <br/><br/><br/>
                    <p class="subheading">Hey """ + poster.name.split(" ")[0] + """,</p>
                    <p class="subheading">Someone wants to let you know that they're interested in one of your listings.</p>
                    <br/><br/>
                    <div class="link">
                        <p class="text"><a href="http://roommatefinder.riceapps.org/user/""" + joiner_netid + """">""" + joiner.name + " [" + joiner_netid + "]" + """</a> sent you a notification that he or she is interested in your listing <a href="http://roommatefinder.riceapps.org/listing/""" + listing_id + """">""" + listing.apartment_name + """</a> that you posted on """ + listing.timestamp + """.</p>
                    </div>
                    <br/>
                    <p class="text">We'll let you two take care of things from here. You can simply reply to this email, and it will be delivered to """ + joiner.name.split(" ")[0] + """'s Rice email address.</p>
                    <br/><br/>
                    <p class="text">Sincerely,</p>
                    <p class="text">The Roommate Finder team, Rice Apps</p>
                    <br/><br/><br/>
                    <p class="footer">ROOMMATE FINDER, A PROJECT OF RICE APPS, 2015</p>
                    <div class="footerlink">
                        <p class="footer"><a href="http://roommatefinder.riceapps.org/about">ABOUT</a> | <a href="http://roommatefinder.riceapps.org/privacy_policy">PRIVACY POLICY</a> | <a href="mailto:kevinlin@rice.edu">CONTACT</a></p>
                    </div>
                    <br/><br/><br/><br/><br/>
                </td>
                <td width="20%"></td>
            </tr>
        </table>
    </body>
</html>
    """

    # Message sent to joiner
    joiner_msg = Message("Roommate Finder - You've sent " + poster.name.split(" ")[0] + " a notification of interest", sender=("Rice Roommate Finder", "roommatefinder@rice.edu"))
    joiner_msg.add_recipient((joiner.name, "" + joiner_netid + "@rice.edu"))
    joiner_msg.html = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" ng-app="roommateFinder">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

        <!--Fonts-->
        <link href='http://fonts.googleapis.com/css?family=Oxygen:400,300,700' rel='stylesheet' type='text/css'>
        <link href='http://fonts.googleapis.com/css?family=Oswald:400,300,700' rel='stylesheet' type='text/css'>

        <style type="text/css">
            * {
                margin: 0;
                padding: 0;
            }
            body {
                background-color: #1F2021;
            }
            p.heading {
                font-family: 'Oxygen', sans-serif;
                font-weight: 700;
                letter-spacing: 1px;
                font-size: 26px;
                color: #E0E0E0;
            }
            p.subheading {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 20px;
                color: #E0E0E0;
            }
            p.text {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 16px;
                color: #E0E0E0;
            }
            p.footer {
                font-family: 'Oxygen', sans-serif;
                font-weight: 300;
                letter-spacing: 1px;
                font-size: 10px;
                color: #B3B3B3;
            }
            .link a:link {
				color: #409AB3;
				text-decoration: none;
			}
			.link a:hover {
				color: #409AB3;
				text-decoration: none;
				border-bottom: 2px solid #409AB3;
			}
			.link a:visited {
				color: #409AB3;
				text-decoration: none;
			}
			.link a:active {
				color: #409AB3;
				text-decoration: none;
			}
            .footerlink a:link {
				color: #B3B3B3;
				text-decoration: none;
			}
			.footerlink a:hover {
				color: #B3B3B3;
				text-decoration: none;
				border-bottom: 1px solid #B3B3B3;
			}
			.footerlink a:visited {
				color: #B3B3B3;
				text-decoration: none;
			}
			.footerlink a:active {
				color: #B3B3B3;
				text-decoration: none;
			}
        </style>
    </head>
    <body>
        <table>
            <tr>
                <td width="20%"></td>
                <td width="60%">
                    <br/><br/>
                    <img src="http://roommatefinder.riceapps.org/static/graphics/logo_email.png" width="375px" height="75px" style="height: 75px; width: 375px;" />
                    <br/><br/><br/>
                    <p class="subheading">Hey """ + joiner.name.split(" ")[0] + """,</p>
                    <p class="subheading">This email confirms that we've sent """ + poster.name.split(" ")[0] + """ a notification that you're interested in one of his or her listings. Here's a copy of the notification we sent """ + poster.name.split(" ")[0] + """:</p>
                    <br/><br/>
                    <div class="link">
                        <p class="text"><a href="http://roommatefinder.riceapps.org/user/""" + joiner_netid + """">""" + joiner.name + " [" + joiner_netid + "]" + """</a> sent you a notification that he or she is interested in your listing <a href="http://roommatefinder.riceapps.org/listing/""" + listing_id + """">""" + listing.apartment_name + """</a> that you posted on """ + listing.timestamp + """.</p>
                    </div>
                    <br/>
                    <p class="text">We'll let you two take care of things from here. You can simply reply to this email, and it will be delivered to """ + joiner.name.split(" ")[0] + """'s Rice email address.</p>
                    <br/><br/>
                    <p class="text">Sincerely,</p>
                    <p class="text">The Roommate Finder team, Rice Apps</p>
                    <br/><br/><br/>
                    <p class="footer">ROOMMATE FINDER, A PROJECT OF RICE APPS, 2015</p>
                    <div class="footerlink">
                        <p class="footer"><a href="http://roommatefinder.riceapps.org/about">ABOUT</a> | <a href="http://roommatefinder.riceapps.org/privacy_policy">PRIVACY POLICY</a> | <a href="mailto:kevinlin@rice.edu">CONTACT</a></p>
                    </div>
                    <br/><br/><br/><br/><br/>
                </td>
                <td width="20%"></td>
            </tr>
        </table>
    </body>
</html>
    """

    mail.send(poster_msg)
    mail.send(joiner_msg)