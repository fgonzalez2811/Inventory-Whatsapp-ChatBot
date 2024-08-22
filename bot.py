import os
import time

from twilio.rest import Client
from flask import Flask, request

from cs50 import SQL


app = Flask(__name__)

@app.route("/", methods=["POST"])
# chatbot logic
def bot():

    # get the last user message:
    user_msg = request.values.get('Body', '')
    
    # get the user whatsapp number:
    sender = request.form['From']

    # Get the car inventory data base:
    db = SQL('sqlite:////workspaces/Inventory-Whatsapp-ChatBot/car_inventory.db')

    # From the database, get the time of the db last update and calculate the elapsed time from that moment to the present:
    update_time = db.execute('SELECT time_stamp FROM time;')[0]['time_stamp']
    elapsed_time = time_ago_from_now(update_time)

    # READ THE USER MESSAGE AND DECIDE WHAT TO LOOK UP IN THE DATABASE:
        
    # Use a match-case switch to tell the bot what to answer based con the user message:
    match user_msg.lower():
        # case if the user asks for the complete stock list:
        case 'stock':
            # Start building the answer about the stock:
            answer = 'Encuentre el inventario completo a continuación:\n\n'
            
            # Query the database for the count of every model:
            query = db.execute('SELECT model, COUNT(*) as count FROM inventory GROUP BY model;')
            
            if query:
                
                # update the answer with every car count in the query:
                for car in query:
                    answer += f"*{car['model']}:* {car['count']}\n"
        
                # Show the time if the last update at the end of the message:
                answer += f'\n_Última actualización {elapsed_time}._\n'
            
            else:
                answer = 'Ocurrió un error consultando el inventario'
            
            # Send the response to the user:
            message = client.messages.create(
            from_='whatsapp:+14155238886',
            body= answer,
            to=sender
            )
            
        # case if the user asks for a particular model.
        case _:           
            answer = 'Cantidad de ' + user_msg.lower() + ' en inventario:\n\n'
            query = db.execute('SELECT model, COUNT(*) as count FROM inventory WHERE model LIKE ? GROUP BY model;', ('%' + user_msg + '%'))
            
            if query:
                for car in query:
                    answer += f"*{car['model']}:* {car['count']}\n"
                
                # Show the time of the last update at the end of the message:
                answer += f'\n_Última actualización {elapsed_time}._\n'
                
                # Send the response to the user:
                message = client.messages.create(
                from_='whatsapp:+14155238886',
                body= answer,
                to=sender
                )
                            
                # Query the database for the list of cars of the model asked by the user:
                list_query = db.execute('SELECT model, color, model_year, prod_month, chasis_num, upholstery FROM inventory WHERE model LIKE ?;', ('%' + user_msg + '%'))

                # initialize an index to count every model added to the answer messages:
                index = 0

                # write answer messages with 10 cars each until every car info is sent:
                while index < len(list_query):

                    # Add the header names to the message:
                    list_answer = '\n*Mes Prod. | Modelo | Color | Chasis | Tapiceria*\n\n'

                    # if the remaining cars are more than 10, add 10 cars info to the message:
                    if (len(list_query) - index) >= 10:
                        for i in range(index, index + 10):
                            index += 1
                            list_answer += f"*{index}.* {list_query[i]['prod_month']} | {list_query[i]['model']} {list_query[i]['model_year'].replace(',','')} | {list_query[i]['color']} | {list_query[i]['chasis_num']} | {list_query[i]['upholstery']}\n\n"

                        # Send the message:
                        message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body= list_answer,
                        to=sender
                        )
                        time.sleep(1)

                    # If the remaining cars are less than 10, add the reamaining cars info to a message and send it:
                    else:
                        for i in range(index, len(list_query)):
                            index += 1
                            list_answer += f"*{index}.* {list_query[i]['prod_month']} | {list_query[i]['model']} {list_query[i]['model_year'].replace(',','')} | {list_query[i]['color']} | {list_query[i]['chasis_num']} | {list_query[i]['upholstery']}\n\n"
                        
                        # Send message:
                        message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body= list_answer,
                        to=sender
                        )
                        time.sleep(1)
                        
                # send a final message anouncing the end of the information:
                message = client.messages.create(
                    from_='whatsapp:+14155238886',
                    body= '_Consulta finalizada._',
                    to=sender
                    )         
                    
            else:
                answer = 'No se encuentran ' + user_msg.lower() + ' en inventario.'
                
                # Send the response to the user:
                message = client.messages.create(
                from_='whatsapp:+14155238886',
                body= answer,
                to=sender
                )
    
    return print('chatbot operation successful')         

# Create a function that returns the time that has passed since a given timestamp.
# This function will be used to get the time since the inventory last update:   
def time_ago_from_now(event_timestamp):
    current_timestamp = time.time()
    time_difference = current_timestamp - event_timestamp

    if time_difference >= 86400:  # 86400 seconds in a day
        days = int(time_difference / 86400)
        if days == 1:
            return "hace 1 día"
        else:
            return f"hace {days} días"
    elif time_difference >= 3600:
        hours = int(time_difference / 3600)
        return f"hace {hours} horas"
    elif time_difference >= 60:
        minutes = int(time_difference / 60)
        return f"hace {minutes} minutos"
    else:
        seconds = int(time_difference)
        return f"hace {seconds} segundos"


if __name__ == "__main__":
    
# Create car_list as a test:
  
    # Get twilio credentials from enviroment variables:
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    
    client = Client(account_sid, auth_token)
    
    app.run()

