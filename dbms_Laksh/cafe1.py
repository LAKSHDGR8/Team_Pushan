import customtkinter
from tkinter import *
from tkinter import messagebox
from datetime import date

app = customtkinter.CTk()
app.title('Cafe')
app.geometry("1000x400") # Adjust size of screen
app.config(bg="#25283b")
app.resizable(True,True)

font1=('Arial',25,'bold')
font2=('Arial',12,'bold')
font3=('Arial',25,'bold')
price_list=[50,40,40]
total_price=0

bill_frame = customtkinter.CTkFrame(app,width=500,height=400,fg_color="#545457")
bill_frame.place(x=800,y=0)

menu_label=customtkinter.CTkLabel(app,text="My Cafe",font=font1,text_color="#FFFFFF",bg_color="#25283b")
menu_label.place(x=230,y=5)

img1=PhotoImage(file=r"DBMS_Naveen/idli_vada.png")
img2=PhotoImage(file=r"DBMS_Naveen/masal.png")
img3=PhotoImage(file=r"DBMS_Naveen/poori.png")

def pay():
    global total_price
    if(customer_entry.get() == ''):
        messagebox.showerror(title="Error",message="Please Entet Your Name :")
    else:
        total_price=int(quantity1_combobox.get())*price_list[0]+int(quantity2_combobox.get())*price_list[1]+int(quantity3_combobox.get())*price_list[2] 
        if(total_price==0):
            messagebox.showwarning(title="Error",message="Please Select Some Dishes: ")
        else:
            name_label=customtkinter.CTkLabel(bill_frame,text=f'Customer Name : {customer_entry.get()}',font=font3,bg_color="#090b17",width=320,anchor=W)
            name_label.place(x=0,y=100)
            
            price_label=customtkinter.CTkLabel(bill_frame,text=f'Total Price : {total_price} $',font=font3,bg_color="#090b17",width=320,anchor=W)
            price_label.place(x=0,y=150)
            
            date_label=customtkinter.CTkLabel(bill_frame,text=f'Bill Date : {date.today()}',font=font3,bg_color="#090b17",width=320,anchor=W)
            date_label.place(x=0,y=200)
            
            
            
def new():
    customer_entry.delete(0,END)
    quantity1_combobox.set(0)
    quantity2_combobox.set(0)
    quantity3_combobox.set(0)
    
    
def save():
    f=open(f'{customer_entry.get()}Bill ', "w")
    f.write(f'Customer Name: {customer_entry.get()}\n')
    f.write(f'Total Price: {total_price} $\n') 
    f.write(f'Bill Date: {date.today()}')
    messagebox.showinfo(title="Saved",message="Bill has been Saved")  
    f.close()
    
img1_label=customtkinter.CTkLabel(app,image=img1,text="Idli Vada\n Price : 50$",font=font2,text_color="#FFFFFF",fg_color="#090b17",width=200,height=200,corner_radius=20,compound=TOP,anchor=N)
img1_label.place(x=30,y=70)

img2_label=customtkinter.CTkLabel(app,image=img2,text="Masal Dosa\n Price : 40$",font=font2,text_color="#FFFFFF",fg_color="#090b17",width=200,height=200,corner_radius=20,compound=TOP,anchor=N)
img2_label.place(x=250,y=70)

img3_label=customtkinter.CTkLabel(app,image=img3,text="Poori\n Price : 40$",font=font2,text_color="#FFFFFF",fg_color="#090b17",width=100,height=200,corner_radius=20,compound=TOP,anchor=N)
img3_label.place(x=500,y=70)

quantity1_combobox=customtkinter.CTkComboBox(app,font=font3,text_color="#000000",fg_color="#FFFFFF",values=('0','1','2','3','4'),state="readonly")
quantity1_combobox.place(x=63,y=220)
quantity1_combobox.set(0)

quantity2_combobox=customtkinter.CTkComboBox(app,font=font3,text_color="#000000",fg_color="#FFFFFF",values=('0','1','2','3'),state="readonly")
quantity2_combobox.place(x=280,y=220)
quantity2_combobox.set(0)

quantity3_combobox=customtkinter.CTkComboBox(app,font=font3,text_color="#000000",fg_color="#FFFFFF",values=('0','1','2','3'),state="readonly")
quantity3_combobox.place(x=500,y=220)
quantity3_combobox.set(0)

customer_label=customtkinter.CTkLabel(app,text="Customer Name",font=font2,text_color="#FFFFFF",fg_color="#25283b")
customer_label.place(x=50,y=300)

customer_entry=customtkinter.CTkEntry(app,font=font2,fg_color="#FFFFFF",text_color="#000000",border_color="#FFFFFF",width=200)
customer_entry.place(x=200,y=300)

pay_button=customtkinter.CTkButton(app,command=pay,text="Pay Bill",font=font2,fg_color="#ad0c78",hover_color="#ad0c78",corner_radius=20,cursor="hand2")
pay_button.place(x=100,y=350)

save_button=customtkinter.CTkButton(app,command=save,text="Save Bill",font=font2,fg_color="#058007",hover_color="#058007",corner_radius=20,cursor="hand2")
save_button.place(x=250,y=350)

new_button=customtkinter.CTkButton(app,command=new,text="New Bill",font=font2,fg_color="#c26406",hover_color="#c26406",corner_radius=20,cursor="hand2")
new_button.place(x=400,y=350)


if __name__ == "__main__":
    app.mainloop()