import os,socket,threading,urllib.parse,http.server,socketserver,tkinter as tk
from datetime import datetime
from tkinter import filedialog as fd,messagebox as mb,ttk
P,S,H,R=9449,[],None,False
def get_ip():
 s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
 try:s.connect(('8.8.8.8',80));ip=s.getsockname()[0];s.close();return ip
 except:s.close()
 try:return socket.gethostbyname(socket.gethostname())
 except:return '127.0.0.1'
def get_dev_name(ip):
 try:return socket.gethostbyaddr(ip)[0]
 except:return "Смартфон/ПК" if ip!="127.0.0.1" else "Этот Компьютер (Тест)"
class Hndl(http.server.BaseHTTPRequestHandler):
 def log_message(self,f,*a):pass
 def do_GET(self):
  global S
  p=urllib.parse.unquote(self.path).lstrip('/')
  fd_dict={os.path.basename(f):f for f in S}
  if p=="":
   self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers()
   html="<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Скачать</title><style>body{font-family:Arial;padding:20px;background:#f4f4f9;} .card{background:white;padding:15px;margin:10px 0;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);display:flex;justify-content:space-between;align-items:center;} a{background:#4CAF50;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;font-weight:bold;}</style></head><body><h2>📥 Доступные файлы:</h2>"
   if not fd_dict:html+="<p style='color:gray;'>Список пуст.</p>"
   for fn,fp in fd_dict.items():
    rs=os.path.getsize(fp);sz=f"{rs/(1024*1024):.2f} MB" if rs>=1024*1024 else f"{rs/1024:.1f} KB"
    html+=f"<div class='card'><div><b>{fn}</b><br><small style='color:gray;'>Размер: {sz}</small></div><a href='/{urllib.parse.quote(fn)}' download>Скачать</a></div>"
   html+="</body></html>";self.wfile.write(html.encode('utf-8'))
   # Меняем статус на ПК строго по вашему ТЗ при заходе с телефона
   name=get_dev_name(self.client_address[0])
   w.after(0,lambda:lbl.config(text=f"Найдено (1) устройство. Имя устройства: {name}\nСайт успешно открыт на телефоне!",fg="green"))
   return
  if p in fd_dict and os.path.exists(fd_dict[p]):
   self.send_response(200);self.send_header("Content-Type","application/octet-stream");self.send_header("Content-Disposition",f'attachment; filename="{urllib.parse.quote(p)}"');self.send_header("Content-Length",str(os.path.getsize(fd_dict[p])));self.end_headers()
   with open(fd_dict[p],'rb') as f:
    while (c:=f.read(4096)):self.wfile.write(c)
   return
  self.send_error(404)
def sel_f():
 global S;f=fd.askopenfilenames()
 if f:
  S=list(f)
  for i in t.get_children():t.delete(i)
  for p in S:
   fn=os.path.basename(p);rs=os.path.getsize(p)
   sz=f"{rs/(1024*1024):.2f} MB" if rs>=1024*1024 else f"{rs/1024:.1f} KB"
   try:dt=datetime.fromtimestamp(os.path.getctime(p)).strftime('%d.%m.%Y %H:%M')
   except:dt="--.--.---- --:--"
   t.insert("",tk.END,values=(sz,fn,dt))
def tgl_srv():
 global R,H
 if not R:
  R=True;lbl.config(text="Статус: Ожидание устройств...",fg="orange");b_srv.config(text="Выключить",bg="#e91e63")
  threading.Thread(target=run_srv,daemon=True).start()
 else:
  R=False
  if H:threading.Thread(target=H.shutdown,daemon=True).start()
  lbl.config(text="Статус приема: Выключен",fg="red");b_srv.config(text="Включить прием",bg="#2196F3")
def run_srv():
 global H
 try:
  socketserver.TCPServer.allow_reuse_address=True
  with socketserver.TCPServer(("0.0.0.0",P),Hndl) as s:H=s;s.serve_forever()
 except:w.after(0,tgl_srv)
w=tk.Tk();w.title("HTTP Передатчик файлов по IP");w.geometry("620x540");w.resizable(False,False)
ttk.Style().theme_use('clam');my_ip=get_ip()
tk.Label(w,text="Введите этот адрес в браузере телефона:",font=("Arial",11,"bold")).pack(anchor="w",padx=15,pady=(15,2))
ed=tk.Entry(w,font=("Arial",11,"bold"),fg="blue",justify="center");ed.insert(0,f"http://{my_ip}:{P}");ed.config(state="readonly");ed.pack(fill="x",padx=15,pady=2)
tk.Button(w,text="📁 Выбрать файлы (можно много)",command=sel_f,bg="#e1e1e1",font=("Arial",11,"bold")).pack(fill="x",padx=15,pady=10)
t=ttk.Treeview(w,columns=("sz","nm","dt"),show="headings",height=6);t.pack(fill="x",padx=15,pady=5)
t.heading("sz",text="ВЕС ФАЙЛА");t.heading("nm",text="ИМЯ ФАЙЛА");t.heading("dt",text="ДАТА-СОЗДАНИЯ ФАЙЛА")
t.column("sz",width=110,anchor="center");t.column("nm",width=300,anchor="w");t.column("dt",width=160,anchor="center")
f_rcv=tk.LabelFrame(w,text=" Результаты сетевого сканирования и обмена ",font=("Arial",9,"bold"),padx=10,pady=5);f_rcv.pack(fill="x",padx=15,pady=5)
lbl=tk.Label(f_rcv,text="Статус приема: Выключен",fg="red",font=("Arial",10,"bold"),justify="left");lbl.pack(side="left",pady=5)
b_srv=tk.Button(f_rcv,text="Включить прием",command=tgl_srv,bg="#2196F3",fg="white",font=("Arial",9,"bold"));b_srv.pack(side="right",pady=5)
w.mainloop()
