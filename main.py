'''
    Pizza purchase aplication with sqlite and tkinter.
'''

#!/usr/bin/env python
__version__ = '0.1'
__author__ = "NAKAMA"

# Packs
from tkinter import Tk,Button,PhotoImage,Label,LabelFrame,W,E,N,S,\
    END,StringVar,Scrollbar,Toplevel,Variable,Listbox,VERTICAL
from tkinter import ttk   # Provides access to the Tk themed widgets.
import sqlite3

class Engine:
    '''
        tkinter engine.
    '''

    db_filename = 'pizza.db'

    def __init__(self,root):
        self.root = root

        ''' create gui. '''
        self.create_left_icon()
        self.create_label_frame()
        self.create_message_area()
        self.create_tree_view()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.view_orders()

        ttk.style = ttk.Style()
        ttk.style.configure("Treeview", font=('helvetica',10))
        ttk.style.configure("Treeview.Heading", font=('helvetica',12, 'bold'))


    def execute_db_query(self, query, parameters=()):
        '''
            execute db query.
        '''

        with sqlite3.connect(self.db_filename) as conn:
            print(conn)
            print('You have successfully connected to the Database')
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result


    def create_left_icon(self):
        '''
            picture
        '''
        photo = PhotoImage(file='logo.png')
        label = Label(image=photo)
        label.image = photo
        label.grid(row=0, column=0)

    def create_label_frame(self):
        ''' create label frame '''
        labelframe = LabelFrame(self.root, text='Create New Order',bg="sky blue",\
                                font="helvetica 10")
        labelframe.grid(row=0, column=1, padx=8, pady=8, sticky='ew')

        Label(labelframe, text='Pizza Type:',bg="green",fg="white")\
              .grid(row=1, column=1, sticky=W, pady=2,padx=15)
        pizza_type = StringVar()
        self.pizza_type_field = ttk.Combobox(labelframe, textvariable=pizza_type)
        self.pizza_type_field['values'] = ["Marinara","Margherita","TurkPizza","PlainPizza"]
        self.pizza_type_field.grid(row=1, column=2, sticky=W, padx=5, pady=2)

        Label(labelframe, text='Size:',bg="brown",fg="white")\
              .grid(row=2, column=1, sticky=W,  pady=2,padx=15)
        pizza_size = StringVar()
        self.pizza_size_field = ttk.Combobox(labelframe, textvariable=pizza_size)
        self.pizza_size_field['values'] = ["small", "medium", "large", "xlarge"]
        self.pizza_size_field.grid(row=2, column=2, sticky=W, padx=5, pady=2)

        # create a list box
        topping_box_values = ['Olives', 'Muhrooms', 'GoatCheese', 'Meat',
                              'Onions', 'Corn', 'Garlic', 'Basil', 'Tomato' ]
        var = Variable(value=topping_box_values)
        Label(labelframe, text='Toppings:',bg="black",fg="white")\
              .grid(row=3, column=1, sticky=W,  pady=2,padx=15)
        self.pizza_topping_field = Listbox(labelframe, listvariable=var,\
                                           height=6, selectmode = "multiple")
        self.pizza_topping_field.grid(row=3, column=2, sticky=W, padx=5, pady=2)

        # link a scrollbar to a list
        self.topping_scrollbar = ttk.Scrollbar(labelframe,
                                               orient=VERTICAL,
                                               command=self.pizza_topping_field.yview)
        self.pizza_topping_field['yscrollcommand'] = self.topping_scrollbar.set
        self.pizza_topping_field.config(yscrollcommand=self.topping_scrollbar.set)
        self.topping_scrollbar.grid(row=3, column=3, sticky="ns")

        Button(labelframe, text='Add to cart',
               command=self.on_add_order_button_clicked,
               bg="blue",fg="white").grid(row=4, column=2, sticky=E, padx=5, pady=5)

    def create_message_area(self):
        ''' create message area '''
        self.message = Label(text='', fg='red')
        self.message.grid(row=3, column=1, sticky=W)

    def create_tree_view(self):
        ''' create tree view '''
        self.tree = ttk.Treeview(height=10,\
                                 columns=("pizza_type","pizza_size","topping"),
                                          style='Treeview')
        self.tree.grid(row=6, column=0, columnspan=3)
        self.tree.heading('#0', text='id', anchor=W)
        self.tree.heading("pizza_type", text='Pizza Type', anchor=W)
        self.tree.heading("pizza_size", text='Pizza Size', anchor=W)
        self.tree.heading("topping", text='Topping', anchor=W)

    def create_scrollbar(self):
        ''' create scrollbar '''
        self.scrollbar = Scrollbar(orient='vertical',command=self.tree.yview)
        self.scrollbar.grid(row=6,column=3,rowspan=10,sticky='sn')

    def create_bottom_buttons(self):
        ''' bottom buttons '''
        Button(text='Delete Selected',
               command=self.on_delete_selected_button_clicked,
               bg="red",fg="white").grid(row=8, column=0, sticky=W)
        Button(text='Modify Selected',
               command=self.on_modify_selected_button_clicked,
               bg="red",fg="white").grid(row=9, column=0, sticky=W)
        Button(text='Place Order',
               command=self.on_place_order_button_clicked,
               bg="blue",fg="white").grid(row=8, column=1, sticky=W)

    def on_add_order_button_clicked(self):
        ''' add '''
        self.add_new_order()

    def on_place_order_button_clicked(self):
        ''' place order '''
        self.place_order()

    def on_delete_selected_button_clicked(self):
        ''' delete '''
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected to delete'
            return
        self.delete_orders()

    def on_modify_selected_button_clicked(self):
        ''' modify '''
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]

        except IndexError as e:
            self.message['text'] = 'No item selected to modify'
            return
        self.open_modify_window()



    def add_new_order(self):
        ''' add new '''
        if self.new_orders_validated():
            query = 'INSERT INTO orders VALUES(NULL,?, ?,?)'
            topping_list_values = ','.join(str(v) for v in self.pizza_topping_field.curselection())
            parameters = (self.pizza_type_field.current(),
                            self.pizza_size_field.current(),
                            topping_list_values)
            self.execute_db_query(query, parameters)
            self.message['text'] = f"New Order {self.pizza_type_field.get()} added."
            self.pizza_type_field.delete(0, END)
            self.pizza_size_field.delete(0, END)
            self.pizza_topping_field.selection_clear(0, END)
            self.view_orders()

        else:
            self.message['text'] = 'Required fields cannot be blank'
            self.view_orders()

    def new_orders_validated(self):
        ''' validate '''
        return self.pizza_type_field.current() != -1 and self.pizza_size_field.current() != -1

    def view_orders(self):
        ''' view '''
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)
        query = 'SELECT * FROM orders ORDER BY id desc'
        order_entries = self.execute_db_query(query)
        for row in order_entries:
            self.tree.insert('', 0, text=row[0], values=(row[1],row[2],row[3]))

    def delete_orders(self):
        ''' delete '''
        self.message['text'] = ''
        selected_query = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM orders WHERE id = ?'
        self.execute_db_query(query, (selected_query,))
        self.message['text'] = f"Order {selected_query} deleted."
        self.view_orders()

    def place_order(self):
        ''' place order '''
        print("place order")

    def open_modify_window(self):
        ''' modify '''
        selected_query = self.tree.item(self.tree.selection())['text']
        old_pizza_type = self.tree.item(self.tree.selection())['values'][0]
        old_pizza_size = self.tree.item(self.tree.selection())['values'][1]
        old_topping_list = self.tree.item(self.tree.selection())['values'][2]
        self.transient = Toplevel()
        self.transient.title('Update Order')

        Label(self.transient, text='Pizza Type:').grid(row=1, column=0)
        pizza_type_field = ttk.Combobox(self.transient, textvariable=StringVar(
            self.transient))
        pizza_type_field['values'] = ["Marinara","Margherita","TurkPizza","PlainPizza"]
        pizza_type_field.current(old_pizza_type)
        pizza_type_field.grid(row=1, column=1)

        Label(self.transient, text='Pizza Size:').grid(row=2, column=0)
        pizza_size_field = ttk.Combobox(self.transient, textvariable=StringVar(
            self.transient))
        pizza_size_field['values'] = ["small", "medium", "large", "xlarge"]
        pizza_size_field.current(old_pizza_size)
        pizza_size_field.grid(row=2, column=1)

        Label(self.transient, text='Toppings:').grid(row=0, column=3)
        topping_box_values = ['Olives', 'Muhrooms', 'GoatCheese', 'Meat',
                              'Onions', 'Corn', 'Garlic', 'Basil', 'Tomato' ]
        var = Variable(value=topping_box_values)
        pizza_topping_field = Listbox(self.transient,listvariable=var,\
                                           height=6, selectmode = "multiple")
        pizza_topping_field.grid(row=1, column=3, sticky=W)
        topping_scrollbar = ttk.Scrollbar(orient=VERTICAL,
                                               command=pizza_topping_field.yview)
        pizza_topping_field['yscrollcommand'] = topping_scrollbar.set
        pizza_topping_field.config(yscrollcommand=topping_scrollbar.set)

        for t in list(str(old_topping_list).replace(" ", "").replace(",", "")):
            pizza_topping_field.select_set(t)
        topping_scrollbar.grid(row=3, column=3, sticky="ns")

        print("test")
        print(pizza_topping_field.curselection())
        topping_list_values = ','.join(str(v) for v in pizza_topping_field.curselection())
        print(topping_list_values)

        Button(self.transient,
               text='Update Order',
               command=lambda: self.update_orders(
                pizza_type_field.current(),pizza_size_field.current(),topping_list_values,
                selected_query)).grid(row=4, column=2, sticky=E
                )

        self.transient.mainloop()

    def update_orders(self, pizza_type, pizza_size, topping_list, order_id):
        """ update """
        print(topping_list)
        query = 'UPDATE orders SET pizza_type=?,pizza_size=?  WHERE id =?'
        parameters = (pizza_type, pizza_size, topping_list, id)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = f"Order {order_id} modified."
        self.view_orders()

def main():
    """ Run root window's main loop"""
    root =Tk()
    root.title('Pizza Aplication')
    root.geometry("1024x800")
    root.resizable(width=False, height=False)
    application = Engine(root)
    root.mainloop()


if __name__ == '__main__':
    main()
