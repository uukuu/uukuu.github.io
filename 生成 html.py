import os
import shutil #移动，复制文件
import tkinter as tk  # 导入tkinter模块。为了方便后续讲解，命名为 tk。
import tkinter.messagebox  # 引入弹窗库，防止解释器弹出报错。


def display_messagebox(name): 
	tk.messagebox.showwarning(title='警告信息',
		message="文件"+name+'不存在')  # 信息警告弹窗，点击确定返回值为 ok
	
def makepath(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)         

aside_menu_margin = 22

from PyPDF2 import PdfReader

def makeMenuHtmlMdDfs(lst,pos,n,margin):
    global directory_str
    res=""
    margin=min(margin,43)
    if pos == n - 1:
        res+=('''           <div class="md-toc-link-wrapper"
						style="padding:0;;display:list-item;list-style:disc;margin-left:{0}px">
						<a href="{1}" class="md-toc-link">
							<p>{2}</p>

						</a>
					</div>
'''.format(margin,"#"+lst[pos][1],lst[pos][2]))
    elif lst[pos + 1][0] == lst[pos][0]:
        res+=('''           <div class="md-toc-link-wrapper"
						style="padding:0;;display:list-item;list-style:disc;margin-left:{0}px">
						<a href="{1}" class="md-toc-link">
							<p>{2}</p>

						</a>
					</div>
'''.format(margin,"#"+lst[pos][1],lst[pos][2]))
        res+=makeMenuHtmlMdDfs(lst,pos+1,n,margin)
    elif lst[pos + 1][0] < lst[pos][0]:
        res+=('''           <div class="md-toc-link-wrapper"
						style="padding:0;;display:list-item;list-style:disc;margin-left:{0}px">
						<a href="{1}" class="md-toc-link">
							<p>{2}</p>

						</a>
					</div>
'''.format(margin,"#"+lst[pos][1],lst[pos][2]))
    elif lst[pos+1][0] > lst[pos][0]:
        res+='''                    <details style="padding:0;;margin-left: {0}px;">
						<summary class="md-toc-link-wrapper">
							<a href="{1}" class="md-toc-link">
								<p style="display: inline;">{2}</p>
							</a>
						</summary>
'''.format(margin-21,"#"+lst[pos][1],lst[pos][2])
        res+=makeMenuHtmlMdDfs(lst,pos + 1,n,margin + 21)
        res+="              </details>\n"
        for i in range(pos+2,n):
            if lst[i][0] < lst[pos][0]:
                break
            if lst[i][0] == lst[pos][0]:
                res+=makeMenuHtmlMdDfs(lst,i,n,margin)
                break
    return res

def makeMenuPdfDfs(pdf,list,margin):
    # global directory_str
    res=""
    margin=min(margin,43)
    for i in range(len(list)):
        message=list[i]
        if isinstance(message, dict):
            if i + 1 < len(list) and not isinstance(list[i + 1],dict):
                res+='''                    <details style="padding:0;;margin-left: {0}px;" >
						<summary class="md-toc-link-wrapper">
							<a href="{1}" class="md-toc-link">
								<p style="display: inline;">{2}</p>
							</a>
						</summary>
'''.format(margin-21,"#cw-pdf-"+str(pdf.get_destination_page_number(message) + 1),message['/Title'])
            else:
                res+=('''                   <div class="md-toc-link-wrapper"
						style="padding:0;;display:list-item;list-style:disc;margin-left:{0}px">
						<a href="{1}" class="md-toc-link">
							<p>{2}</p>

						</a>
					</div>
'''.format(margin,"#cw-pdf-"+str(pdf.get_destination_page_number(message) + 1),message['/Title']))
        else:
            res+=makeMenuPdfDfs(pdf,message,margin+21)
            res+=("             </details>\n")
    return res

def makeMenuJiaocaiPdfDfs(pdf,list,margin):
    # global directory_str
    res=""
    margin=min(margin,43)
    for i in range(len(list)):
        message=list[i]
        if isinstance(message, dict):
            if i + 1 < len(list) and not isinstance(list[i + 1],dict):
                res+='''                    <details style="padding:0;;margin-left: {0}px;" >
						<summary class="md-toc-link-wrapper">
							<a href="{1}" class="md-toc-link">
								<p style="display: inline;">{2}</p>
							</a>
						</summary>
'''.format(margin-21,"#cw-pdf-"+str(pdf.get_destination_page_number(message) + 1),message['/Title'])
            else:
                res+=('''                   <div class="md-toc-link-wrapper"
						style="padding:0;;display:list-item;list-style:disc;margin-left:{0}px">
						<a href="{1}" class="md-toc-link">
							<p>{2}</p>

						</a>
					</div>
'''.format(margin,"#cw-pdf-"+str(pdf.get_destination_page_number(message) + 1),message['/Title']))
        else:
            res+=makeMenuJiaocaiPdfDfs(pdf,message,margin+21)
            res+=("             </details>\n")
    return res

name_list = []

for i in range(10000):
    if not os.path.exists('./pre-posts/'+str(i)):
        continue
    for j in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        if not os.path.exists('./pre-posts/'+str(i)+'/'+str(j)):
            continue
        for k in range(31):
            kk=k+1
            kk=str(kk)
            if len(kk)==1:
                kk='0'+kk
            now_path='./pre-posts/'+str(i)+'/'+str(j)+'/'+str(kk)
            if os.path.exists(now_path):
                for z in os.listdir(now_path):
                    name_list.append([now_path,z])

print(name_list)

time_dic={}
time_id={}
for i in name_list:
    k = i[0].split('/')
    time=k[-3]+'-'+k[-2]+'-'+k[-1]
    if time not in time_dic:
        time_dic[time]=0
    time_dic[time]+=1
    time_id[i[1]]=time_dic[time]

name_list.sort(reverse = True)
# 处理 tag 链接

for i in name_list:
    break

# 处理 index.html

# <a href="#">tag1</a>,<a href="#">tag2</a>
link_tag=["算法竞赛","数学"]
def get_tag(s):
    if s == "无":
        return ""
    s = s.split(',')
    fg = 0
    res = ""
    for i in s:
        if fg == 1:
            res += ','
        if i in link_tag:
            res+='<a href="{0}">{1}</a>'.format("./pages/"+i+".html",i)
        else:
            res+='<p style="display:inline;">{0}</p>'.format(i)
        fg = 1
    return res

def make_index():
    file_index=open("./pre-index.html","r",encoding='utf-8')
    file_out=open("./index.html","w",encoding='utf-8')
    flag = 0
    for i in file_index.readlines():
        if "<!-- 正文开始 -->" in i:
            flag = 1
            file_out.write("<!-- 正文开始 -->\n")
            for j in name_list:
                k=j[1].split('-')
                date=j[0].split('/')
                if len(k) == 1:
                    k.append("无")
                s = '''          <article class="show">
                    <div class="mainpart-title">
                    <a href="{2}">{0}</a>
                    </div>
                    <div class="mainpart-meta">
                        <div class="mainpart-meta-time">
                            <img src="./icon/icon_time.svg" class="a-line mainpart-meta-icon"/>
                            <p class="a-line">{1}</p>
                        </div>
                        <div class="a-line mainpart-meta-divide">|</div>
                        <div class="mainpart-meta-tag">
                            <img src="./icon/标签.png" class="a-line mainpart-meta-icon"/>
                            {3}
                        </div>
                    </div>
                    <div class="mainpart-abstract">
                        摘要：
                    </div>
                </article>
    '''.format(k[0],date[-3]+'-'+date[-2]+'-'+date[-1],"./posts/"+date[-3]+"/"+date[-2]+"/"+date[-1]+"/"+str(time_id[j[1]])+".html",get_tag(k[1]))
                file_out.write(s)
        if flag == 1 and "<!-- 正文结束 -->" in i:
            flag = 0
        if flag == 0:
            file_out.write(i)

    file_out.close()

# 教材界面

def make_jiaocai():
    file_index=open("./pre-pages/pre-pages.html","r",encoding='utf-8')
    jiaocai_list=[]
    for i in os.listdir('./pre-posts/教材'):
        filename=i.split('.')
        if(filename[-1]!='pdf'):
            continue
        filename=filename[0]
        jiaocai_list.append(filename)
        path="./pre-posts/教材"
        path_out="./posts/教材/"+filename+".html"
        makepath("./posts/教材/")
        # if os.path.exists(path+"/"+filename+"/"+"反色.pdf"):
        #     shutil.copy(path+"/"+filename+"/"+"反色.pdf","./posts/"+k[0]+"/"+k[1]+"/"+str(time_id[filename])+"-反色.pdf")
        shutil.copy(path+"/"+filename+".pdf","./posts/教材/"+filename+".pdf")
        file_out=open(path_out,"w",encoding="utf-8")
        file_muban=open("./pre-pages/posts-jiaocai-head.html","r",encoding="utf-8")
        
        pdf = PdfReader(path+"/"+filename+".pdf")
        # print(pdf)
        menu = pdf.outline
        # print(menu)
        for j in file_muban.readlines():
            if "<!-- menu -->" in j:
                file_out.write("            <div id=\"md-toc\">\n")
                str=makeMenuJiaocaiPdfDfs(pdf,menu,aside_menu_margin,)
                if str=="":
                    file_out.write("本pdf无目录")
                else:
                    file_out.write(str)
                # print(str)
                file_out.write("            </div>\n")
            else:
                file_out.write(j)
        file_muban.close()
        code_count = 0
        flag = 0
        file_out.write("            <div id=\"canvas\"></div>\n")
        file_out.write("        </div>\n")
        file_out.write('''        <script>
                loadPDF("{0}");
                get_height()
            </script>
    '''.format("./"+filename+".pdf"))
        file_muban=open("./pre-pages/posts-foot.html","r",encoding="utf-8")
        file_out.write(file_muban.read())
        file_out.close()
        file_muban.close()
    # print(jiaocai_list)
    # return
    file_out=open("./pages/jiaocai.html","w",encoding='utf-8')
    flag = 0
    for i in file_index.readlines():
        if "<!-- 正文开始 -->" in i:
            flag = 1
            file_out.write("<!-- 正文开始 -->\n")
            for j in jiaocai_list:
                k=j.split('-')
                if len(k) == 1:
                    k.append("无")
                s = '''          <article class="show">
                    <div class="mainpart-title">
                    <a href="{1}">{0}</a>
                    </div>
                    <div class="mainpart-meta">
                        <div class="mainpart-meta-tag">
                            <img src="../icon/标签.png" class="a-line mainpart-meta-icon"/>
                            {2}
                        </div>
                    </div>
                </article>
    '''.format(k[0],"../posts/教材/"+j+".html",get_tag(k[1]))
                file_out.write(s)
        if flag == 1 and "<!-- 正文结束 -->" in i:
            flag = 0
        if flag == 0:
            file_out.write(i)

    file_out.close()

# 处理文章 html


def make_post_html(path,filename):
    # print(path)
    f=open(path+"/"+filename+"/"+filename+".html","r",encoding='utf-8')
    s=f.readlines()
    f.close()
    n=len(s)
    start = 0
    for i in range(n):
        if '<div class="crossnote markdown-preview  ">' in s[i]:
            start = i
            break
    # print("start",start,n)
    fmd=open(path+"/"+filename+"/"+filename+".md","r",encoding='utf-8')
    smd=fmd.readlines()
    fmd.close()
    lst1 = []
    for i in smd:
        for j in range(6,0,-1):
            tmp="#"*j
            if tmp in i:
                    
                lst1.append([j,i[j+1:],0])
                if "ignore" in i and "true" in i:
                    lst1[-1][2]=-1
                break
    lst = []
    cnt = 0
    for i in s[start+1:]:
        for j in range(1,7):
            if ("<h"+str(j)) in i:
                if lst1[cnt][2] != -1:
                    l = 3
                    leni=len(i)
                    while l < leni:
                        if i[l-4:l] == "id=\"":
                            break
                        l += 1
                    r = l
                    while r < leni:
                        if i[r] == "\"":
                            break
                        r += 1
                    nowid=i[l:r]
                    l = r
                    while l < leni:
                        if i[l-1] == '>':
                            break
                        l += 1
                    r = l
                    while r < leni:
                        if i[r] == '<':
                            break
                        r += 1
                    nowname=i[l:r]
                    lst.append([j,nowid,nowname])
                cnt += 1
                break
    k = path.split('/')
    print(k)
    path_out="./posts/"+k[-3]+"/"+k[-2]+'/'+k[-1]+"/"+str(time_id[filename])+".html"
    makepath("./posts/"+k[-3]+"/"+k[-2]+'/'+k[-1])
    file_out=open(path_out,"w",encoding="utf-8")
    file_muban=open("./pre-pages/posts-head.html","r",encoding="utf-8")
    for i in file_muban.readlines():
        if "<!-- menu -->" in i:
            file_out.write("            <div id=\"md-toc\">\n")
            file_out.write(makeMenuHtmlMdDfs(lst,0,len(lst),aside_menu_margin))
            file_out.write("            </div>\n")
        else:
            file_out.write(i)
    file_muban.close()
    code_count = 0
    flag = 0
    for i in s[start+1:]:
        if "</body>" in i:
            break
        if "<h1" in i and flag == 0:
            leni = len(i)
            for j in range(leni):
                if i[j]=='>' and flag == 0:
                    flag=1
                    file_out.write(' style="text-align: center;"')
                file_out.write(i[j])
        elif "<pre" in i:
            file_out.write('<div class="wrap-collabsible">\n	<input id="collapsible' + str(code_count) + '"class="toggle" type="checkbox">\n	<label for="collapsible' + str(code_count) + '" class="lbl-toggle">Code</label>\n	<div class="collapsible-content">\n	  <div class="content-inner">\n')
            file_out.write(i)
            code_count += 1
        elif "</pre" in i:
            leni = len(i)
            for j in range(leni):
                if i[j-6:j] == "</pre>":
                    file_out.write("</div></div></div>")
                file_out.write(i[j])
        else:
            file_out.write(i)
    file_muban=open("./pre-pages/posts-foot.html","r",encoding="utf-8")
    file_out.write(file_muban.read())
    file_out.close()
    file_muban.close()


def make_post_pdf(path,filename):
    k=path.split('/')
    path_out='./posts/'+k[-3]+"/"+k[-2]+'/'+k[-1]+"/"+str(time_id[filename])+".html"
    makepath("./posts/"+k[-3]+"/"+k[-2]+'/'+k[-1])
    # if os.path.exists(path+"/"+filename+"/"+"反色.pdf"):
    #     shutil.copy(path+"/"+filename+"/"+"反色.pdf","./posts/"+k[0]+"/"+k[1]+"/"+str(time_id[filename])+"-反色.pdf")
    shutil.copy(path+"/"+filename+"/"+filename+".pdf","./posts/"+k[-3]+"/"+k[-2]+'/'+k[-1]+"/"+str(time_id[filename])+".pdf")
    file_out=open(path_out,"w",encoding="utf-8")
    file_muban=open("./pre-pages/posts-head.html","r",encoding="utf-8")
    
    pdf = PdfReader(path+"/"+filename+"/"+filename+".pdf")
    # print(pdf)
    menu = pdf.outline
    # print(menu)
    for i in file_muban.readlines():
        if "<!-- menu -->" in i:
            file_out.write("            <div id=\"md-toc\">\n")
            file_out.write(makeMenuPdfDfs(pdf,menu,aside_menu_margin))
            file_out.write("            </div>\n")
        else:
            file_out.write(i)
    file_muban.close()
    code_count = 0
    flag = 0
    file_out.write("            <div id=\"canvas\"></div>\n")
    file_out.write("        </div>\n")
    file_out.write('''        <script>
	    	loadPDF("{0}");
            get_height()
	    </script>
'''.format("./"+str(time_id[filename])+".pdf"))
    file_muban=open("./pre-pages/posts-foot.html","r",encoding="utf-8")
    file_out.write(file_muban.read())
    file_out.close()
    file_muban.close()

make_index()
make_jiaocai()
for filename in name_list:
    if not os.path.exists(filename[0]+"/"+filename[1]+"/"+filename[1]+".html") and not os.path.exists(filename[0]+"/"+filename[1]+"/"+filename[1]+".pdf"):
        display_messagebox(filename[1]+".html/.pdf")
        continue
    if os.path.exists(filename[0]+"/"+filename[1]+"/"+filename[1]+".html"):
        make_post_html(filename[0],filename[1])
    elif os.path.exists(filename[0]+"/"+filename[1]+"/"+filename[1]+".pdf"):
        make_post_pdf(filename[0],filename[1])