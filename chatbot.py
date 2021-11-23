#nott-a-code
import pandas as pd
import csv
import datetime

class Order:
    #data
    data = pd.read_excel('Food List.xlsx', sheet_name = 'Food data', header = 0)
    data_d = data.to_dict()

    #options
    delivery_opt = pd.DataFrame({'delivery_service': ['no','yes']})
    stall_opt = pd.DataFrame({'stall_name': data['stall_name'].unique()})
    item_opt = pd.DataFrame({})
    yes_no_opt = ['yes','no']

    def __init__(self, delivery=None, stall=[], item={'item':[],'qty':[],'RM':[]},
                done=None, remark=[], time = None):
        self.delivery = delivery
        self.stall = stall
        self.item = item
        self.done = done
        self.remark = remark
        self.time = time

    def __str__(self):
        ret = '\n' +pd.DataFrame(self.item).to_string(index=False) #item name
        ret += '\n\ntotal: RM ' + str(sum(self.item['RM']))
        ret += '\ndelivery: ' +  self.delivery[0] 
        ret += '\nremark: ' + ' '.join(self.remark) + '\n'
        return ret

    #setter
    def set_delivery(self,inpt):
        ret = False
        if len(inpt) ==  1 and inpt[0] in self.yes_no_opt: #guardian code
            ret, self.delivery = True, inpt
        return ret
        
    def set_stall(self, inpt):
        ret, inpt =  False, list(set(inpt)) #remove duplicates
        if all([i in self.stall_opt.index for i in inpt]): #guardian code
            ret, self.stall =True, inpt
        return ret

    def set_item(self, inpt):
        ret = False
        if all([inpt[i] in item_opt.index for i in range(0,len(inpt),2)]) and len(inpt)%2 == 0: #guardian code
            for i in range(0,len(inpt),2):
                item_i = item_opt.iloc[[inpt[i]]]['item_name'].values[0]
                #update quantity
                if item_i in self.item['item']:
                    j = 0 
                    while item_i != self.item['item'][j] and j<len(self.item['item']): j += 1 #locate item index
                    if inpt[i+1]:
                        self.item['qty'][j] = inpt[i+1]
                        price_j = item_opt.loc[item_opt['item_name']==self.item['item'][j]]['price'].values[0]
                        self.item['RM'][j] = self.item['qty'][j]*price_j
                    else:
                        self.item['item'].pop(j)
                        self.item['qty'].pop(j)
                        self.item['RM'].pop(j)

                #add item
                elif inpt[i+1]:
                    self.item['item'] += [item_i]
                    self.item['qty'] += [inpt[i+1]]
                    self.item['RM'] += [inpt[i+1]*item_opt.iloc[[inpt[i]]]['price'].values[0]]
            ret = True
        else: ret = False
        return ret

    def set_done(self,inpt):
        ret = False
        if 'no' in inpt:
            self.done = inpt
            ret = True
        return ret
        
    def set_remark(self,inpt):
        self.remark += [str(i) for i in inpt]
        return True


    def menu(self):
        """
        input: order object
        output: string of menu
        function: generate menu
        """
        #conditon to generate menu
        selected_delivery = self.delivery[0]
        selected_stall = self.stall_opt.iloc[self.stall] 
            
        #selected row
        global item_opt
        item_opt = pd.merge(self.data,selected_stall, on = 'stall_name') #select store
        if self.delivery[0] == 'yes': #select service
            item_opt = item_opt.loc[item_opt['delivery_service']==selected_delivery]
        item_opt.reset_index(drop=True, inplace = True)
        

        #convert to string
        resp = ''
        for i in self.stall:
            stall_name = self.stall_opt['stall_name'][i]
            resp += '\n\n' + str(stall_name) + '\n' 
            resp += str(item_opt.loc[item_opt['stall_name']==stall_name,['item_name','price']])
        resp += '\n00 back'
        return resp
         

def chat():
    order = Order()
    back = '\n00: BACK'
    resp = 'Hi, welcome to cafeteria'
    resp1 = 'Would you like to have delivery service? (yes/no)'
    resp2 = 'What stall(s) you would like to order from?\n{}\n00 back\n(please reply in number)'
    resp3 = 'What item(s) you would like to order?{}\n(please reply in number: item no, item quantity)' 
    resp4 = 'Is there anything else you would like to order?\nadded item:\n{}'
    resp5 = 'Anything to remark?'
    resp6 = '\nbot: Thank you for your order.\nHere is your order summary:{}'
    back = ['00']

    while True:
        print('\nbot:',resp)#bot output
        inpt = tokenize_input(input('you: ').lower())#user input
        #delivery

        if not bool(order.delivery):
            resp = resp1
            if order.set_delivery(inpt):
                resp = resp2.format(order.stall_opt.to_string(header=False))

        #stall
        elif not bool(order.stall):
            if inpt == back:
                order.delivery = []
                resp = resp1
            elif order.set_stall(inpt): 
                resp = resp3.format(order.menu())

        #done
        elif not bool(order.done):
            if inpt == back:
                order.stall = []
                order.item = {'item':[],'qty':[],'RM':[]}
                resp = resp2.format(order.stall_opt.to_string(header=False))
            if order.set_done(inpt):
                resp = resp5
            elif order.set_item(inpt):
                resp4_data = pd.DataFrame(order.item)
                resp = resp4.format(resp4_data.to_string(index=False) if not resp4_data.empty else '[EMPTY]')

        #summary 
        elif not bool(order.remark) and bool(order.done):
            if inpt == back:
                order.done = []
                resp = resp4.format(resp4_data.to_string(index=False) if not resp4_data.empty else '[EMPTY]')
            else:
                order.set_remark(inpt)
                order.time = datetime.datetime.now()
                resp = resp6.format(order)
                print(resp)
            
                #output data in csv
                with open('order.csv','w') as file:
                    writer = csv.writer(file)
                    for i in range(len(order.item['item'])):
                        writer.writerow([order.item['item'][i],order.item['qty'][i],order.item['RM'][i]
                        ,order.delivery,order.time])
                return


def tokenize_input(inpt):
    """
    input: a stirng
    output: a list of string
    function: remove symbol and extra spaces
    """
    ret = ''
    for i in range(len(inpt)):
        #add alphabet and number
        if inpt[i].isalnum(): ret += inpt[i]

        #add space if: 
        #1. charater is a space or symbol 
        #2. following character is numeric or alphabet 
        #3. length of return string >0
        elif (i != len(inpt)-1  and 
            (inpt[i].isspace() or inpt[i].isalnum() == False) #1
            and inpt[i+1].isalnum() and len(ret)>0):  #2 & 3
            ret += ' '
    
    ret = ret.split(' ') #split string into list
    ret = [int(ret[i]) if ret[i].isnumeric() and ret[i] != '00' else str(ret[i]) for i in range(len(ret))] #convert numeric string to int
    return ret
    
chat()

#export data 

#short-coming 
#1. linear flow 
# delivery servcie --> stall --> item --> comfirm

#strategies to upscale:
#1. Mechine learning to identify query
#2. stall business hour
#3. serving 


