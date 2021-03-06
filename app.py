from bs4 import BeautifulSoup as bs
import requests
from urllib.request import urlopen as ureq
from flask import Flask ,render_template,request
from pandas import to_datetime
from flask_cors import cross_origin
from numpy import timedelta64
import datetime
import logging
import plotly
import pymongo as mg
import plotly.graph_objects as go
import json


DBlogger=logging.getLogger('Database')

DBlogger.setLevel(logging.DEBUG)

formatter=logging.Formatter('%(asctime)s:%(name)s: %(message)s')

file_handeler=logging.FileHandler('Database.log')

file_handeler.setLevel(logging.ERROR)

file_handeler.setFormatter(formatter)

DBlogger.addHandler(file_handeler)
"""Stream Handler To Get Logs on Consol"""
stream_handler=logging.StreamHandler()
stream_handler.setFormatter(formatter)
DBlogger.addHandler(stream_handler)


app=Flask(__name__)





# logging.basicConfig(filename='Main.log',level=logging.DEBUG,format='%(asctime)s:%(name)s: %(message)s')


# search="iphone7"

def get_product_highlights(box):
    lst=[]
    highlights=box.find_all('li',{'class':'_21Ahn-'})
    for i in range(len(highlights)):
        lst.append(highlights[i].text)
    return lst

def get_pie_chart(rating_list):
    labels = ['5 Stars', '4 Stars', '3 Stars', '2 Stars','1 Stars']
    values=rating_list
    data = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4,hoverinfo='label+value',title='User Rating')])
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

"""Function to get the list of reviews"""

def get_review(commentsbox ,search,flag=True):
    reviews = []
    for comment in commentsbox[:-1]:
        try:
            name = comment.find_all('p', {"class": "_2sc7ZR _2V5EHH"})[0].text
            # print("Name: ",name)
        except:
            name = "No user name found !"

        try:
            if(flag==True):
                rating = comment.div.div.div.div.text[0]

            else:
                rating = comment.div.div.div.div.text

        except:
            rating = 'There is no rating given by this user !'
        try:
            heading = comment.div.div.div.p.text

        except:
            heading = 'No Heading found for this review !'

        try:
            comment_body = comment.find_all('', {"class": 't-ZTKy'})[0].text
            if(comment_body.endswith('READ MORE')):
                comment_body=comment_body[:comment_body.find('READ MORE')]
            else:
                comment_body=comment_body

        except:
            comment_body = "No comments given by user !"

        """To get the date since user using this device !"""
        try:
            dt=comment.find_all('p', {'class': "_2sc7ZR"})[1].text
            print(dt)
            if("months" in dt):
                using_since = int(dt[:dt.find('months')])
                # print(using_since)
            else:
                dt=to_datetime(dt)
                today = to_datetime(datetime.datetime.today().strftime('%Y-%m-%d'))
                using_since=int((today-dt)/timedelta64(1,'M'))

                # print(using_since)

            # print(using_since)
            # buyed_on = comment.find_all('p', {'class': "_2sc7ZR"})[1].text
            # print(buyed_on)

        except:
            using_since = "No information present !"

        my_dict = {"Product": search, "Name": name, "Rating": rating, "CommentHead": heading, "Comment": comment_body,'Using Since':str(using_since)+" months"}

        reviews.append(my_dict)
    return(reviews)

""""Function to get the product info """

def get_product_info(temp_product_page,search,product_link):
    product_info=[]
    try:
        product_name=temp_product_page.find_all('span',{'class':"B_NuCI"})[0].text
        product_name=product_name[:product_name.find('(')]
        # print(product_name)
    except:
        product_name=search

    try:
        product_overall_rating=temp_product_page.find('span',{'class':'_1lRcqv'}).div.text
        # print(product_overall_rating)
    except:
        product_overall_rating="No Rating Available !"

    try:
        product_seller=temp_product_page.find_all('div',{'class':'_1RLviY'})[0].text
        product_seller_rating=product_seller[-3:]
        product_seller=product_seller[:-3]
        # print(product_seller_rating)
        # print(product_seller)
    except:
        product_seller='No Information Available About Product Seller'
        product_seller_rating='No Information Available About Product Seller Rating'


    #scrapping the image url from flipkart
    try:
        # _396cs4
        # _2amPTt
        # _3qGmMb
        # _3exPp9
        product_image_url = temp_product_page.find_all('div', {'class': 'q6DClP'})[0].attrs['style']
        product_image_url=product_image_url[product_image_url.find('(')+1:-1].replace('128','352')
        # print(product_image_url)

    except:
        product_image_url = 'No image availbel for ' + search

    try:
        product_price=temp_product_page.find_all('div',{"class":'_30jeq3 _16Jk6d'})[0].text
        # print(product_price)
    except:
        product_price='Not available'

    try:
        actual_product_price=temp_product_page.find_all('div',{'class':'_3I9_wc _2p6lqe'})[0].text
        # print(actual_product_price)
    except:
        actual_product_price='Not available'

    try:
        discount_on_product=temp_product_page.find_all('div',{'class':'_3Ay6Sb _31Dcoz'})[0].text
        # print(discount_on_product)
    except :
        discount_on_product='Not available'
    try:
        available_offer=temp_product_page.find_all('div',{'class':'WT_FyS'})[0].text
        available_offer=available_offer.replace('T&C','\n').replace('View Plans','')
        # print(available_offer)

    except:
        available_offer='No Offer available for this product'
        # print(available_offer)

    try:
        currently_available=temp_product_page.find_all('button',{'class':'_2KpZ6l _2U9uOA ihZ75k _3AWRsL'})[0].text
        # print(currently_available)
        if(currently_available==' BUY NOW'):
            currently_available='Yes'
        else:
            currently_available='Out Of Stock'
        # print(currently_available)
    except:
        currently_available = 'Out Of Stock'
        # print(currently_available)
    try:
        product_warranty=temp_product_page.find_all('div',{'class':'_352bdz'})[0].text.replace('Know More','')
        # print(product_warranty)
    except:
        product_warranty='No Information Available'
    #
    # try:
    #     product_specifications=temp_product_page.find_all('div',{'class':"_1UhVsV"})[0].text.split(',')
    #     print(product_specifications)
    # try:
    #     product_highlights=temp_product_page.find_all('div',{'class':'_2418kt'})[0].text.split('|')
    #     # print(product_highlights)
    #
    # except :
    #     product_highlights='No Highlights available'
    try:
        easy_payment_options=temp_product_page.find_all('div',{'class':'_250Jnj'})[0].text
        # print(easy_payment_options)
    except:
        easy_payment_options="No Information Available"

    mydict={"Product Name":product_name,"Product link":product_link,"Product Price":product_price,"Actual Product Price":actual_product_price,"Discount":discount_on_product,'currently_available':currently_available,"Product Image Url":product_image_url,"Produtct Seller":product_seller,"Seller Rating":product_seller_rating,"Product Rating":product_overall_rating,"Available_Offer":available_offer,"Easy Payment Options":easy_payment_options}

    product_info.append(mydict)

    return product_info

@cross_origin()
@app.route("/",methods=["GET","POST"])
def homepage():
    return render_template('index.html')



@app.route("/about",methods=["GET","POST"])
def about():
    return render_template('about.html')

@app.route('/scrap',methods=["POST"])
def scrap():
    if request.method=="POST":
        search=request.form["search_content"].replace(' ','')
        try:
            url = "https://www.flipkart.com/search?q=" + search
            uclient = ureq(url)
            # print(uclient)
            flipkartpage = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartpage, 'html.parser')
            # print(flipkart_html)
            # _2pi5LC col-12-12 this class has been change with recent one _1AtVbE col-12-12
            bigbox = flipkart_html.findAll('div', {'class': '_1AtVbE col-12-12'})
            # print('bigbox',bigbox)
            del bigbox[0:3]
            box = bigbox[0]
            product_highlights=[]
            product_detail=[]

            # print(product_highlights)
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            # print(product_link)
            product_open_page = requests.get(product_link)
            product_html = bs(product_open_page.text, 'html.parser')
            product_highlights.append(get_product_highlights(product_html))
            try:
                rating = product_html.find_all('div', {"class": "_1uJVNT"})
                rating_list = []
                for i in range(len(rating)):
                    # print(type(rating[i].text))
                    rating_list.append(int(rating[i].text.replace(',', '')))
                pie_chart=get_pie_chart(rating_list)

            except Exception as e:
                print(e)
            product_detail.extend(get_product_info(product_html,search,product_link))

            reviews=[]
            """Conncecting with DataBase"""
            try:
                db_connetion=mg.MongoClient("mongodb+srv://scrapper:12345@scrapperdb.p8wac.mongodb.net/scrapper?retryWrites=true&w=majority")
                # print(db_connetion.test)

            except Exception as e:
                DBlogger.exception(e)
                # print(e)
            # print(db_connetion)
            # Connecting To DataBase
            try:
                db=db_connetion['Scrapper']
                check=db[search].find({})


                if(check.count()>0):
                    reviews=list(check)
                    # print(reviews)
                    # print('yes')
                    return render_template('result_page.html',product_detail=product_detail,reviews=reviews,product_highlights=product_highlights,pie_chart=pie_chart,total_reviews_=len(reviews))
                else:
                    # print("nothing")
                    # try:
                    #     # doc=db[search]
                    #     # file_name=search+'.csv'
                    #     # fl=open(file_name,"w")
                    #     # headers= "Product, Custmer Name, Rating, CommentHead, Comment, Using Since"
                    #     # fl.write(headers)
                    #     # print(fl)
                    # except Exception as e:
                    #     DBlogger.exception(e)

                        # print(e)



                    #To get the total reviews of the product
                    try:
                        total_reviews=int(product_html.find_all('div',{'class':"_3UAT2v _16PBlm"})[0].text.replace('All','').replace('reviews',''))
                    except:
                        total_reviews=0



                    # To get the next review page and to get generating url for the review
                    if(total_reviews>10):
                        next_link=product_html.find_all('a',{'class':"col-3-12 hXkZu- _1pxF-h"})[0].attrs['href']
                        next_review_link="https://www.flipkart.com"+next_link[:next_link.find('&')]

                        next_review_page=requests.get(next_review_link)
                        next_page_html=bs(next_review_page.text,'html.parser')
                        mx=next_page_html.find_all('div',{'class':'_2MImiq _1Qnn1K'})
                        for i in range(len(mx)):
                            temp_max_reviews=mx[i].span.text
                            generating_link=mx[i].a['href']

                            #This link will be used to get all liks of the another pages of reviews

                            generating_link=generating_link[:-1]
                            # print(generating_link)

                        max_reviews=int(temp_max_reviews[temp_max_reviews.find('of')+2:])
                        # print(max_reviews)

                    else:
                        commentsbox = product_html.find_all('div', {"class": "_16PBlm"})

                    # To check the count of the reveiws
                    # reviews=[]
                    try:

                        # reviews+= get_review(commentsbox)
                        # print(len(reviews))
                        # print(reviews)
                        # x=len(reviews)

                        if(len(reviews)<501 and total_reviews>10):
                            for i in range(1,max_reviews+1):
                                if(len(reviews)>=500):
                                    # print('Before End reviews: ',len(reviews))
                                    break

                                else:
                                    #Iterating over Review pages to find the url of reviews of perticular product

                                    next_review_generating_link="https://www.flipkart.com"+generating_link+str(i)
                                    # print(next_review_generating_link)
                                    temp_review_page=requests.get(next_review_generating_link)
                                    temp_review_page_html=bs(temp_review_page.text,'html.parser')
                                    temp_comment_box=temp_review_page_html.find_all('div',{'class':'_1AtVbE col-12-12'})
                                    temp_reveiew_list=get_review(temp_comment_box,search)
                                    temp_reveiew_list= temp_reveiew_list[4:]
                                    reviews.extend(temp_reveiew_list)

                        elif(len(reviews)<501 and total_reviews<10):
                            temp_reveiew_list=get_review(commentsbox,flag=False)
                            reviews.extend(temp_reveiew_list)
                            # print(len(reviews))
                        print(len(reviews))
                        """To Insert The Data Into Database"""
                        try:
                            col_name=db[search]
                            DBlogger.info('New collection Creted as {}'.format(col_name))
                            col_name.insert_many(reviews)
                            return render_template('result_page.html', product_detail=product_detail, reviews=reviews,
                                                   product_highlights=product_highlights, pie_chart=pie_chart,
                                                   total_reviews_=len(reviews))
                            DBlogger.info("{} Added To {} Collection".format(len(reviews),col_name))

                            # print('Sucess !')
                        except Exception as e:
                            DBlogger.exception(e)
                            # print(e)


                        # df=DataFrame(reviews)
                        # df.to_csv(file_name)







                    except Exception as e:
                        DBlogger.exception(e)
                        # print(e)
            except Exception as e:
                DBlogger.exception(e)

                print(e)

            # return render_template("results.html", reviews=reviews)
        except Exception as e:
            logging.debug(e)
            print(e)




if __name__=="__main__":
    app.run(debug=True)