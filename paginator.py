from jobplace.models import ReservationModel#PublisherModel,AuthorModel,LibraryModel,BookModel,CustomUser,ReservationModel,HistoryModel,CommentModel
from jobplace.forms import LoginForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pure_pagination.mixins import PaginationMixin


def pagination(result,user):
    #-------- ページネーション前処理
    result_list = [[i.id,i.images,i.book,i.author.author,i.publisher.publisher,i.year,0] for i in result]
    all_reservation = ReservationModel.objects.all().select_related('book').select_related('user')
    all_reservation2 = [[i.book.id,i.user.username,i.book.book,i.book.author,i.book.publisher,i.book.year,i.end_date,i.limited_date,i.status] for i in all_reservation]
    
    for i in result_list:
        for j in all_reservation2:
            if i[0] == j[0]:
                i[6] += 1
    
    reserved_list = [i[0] for i in all_reservation2 if i[1] == str(user) and i[-3] != None] #貸出し
    tori_list = [i[0] for i in all_reservation2 if i[1] == str(user) and i[-1] == 'T'] #取り置き
    borrow_list = [i[0] for i in all_reservation2 if i[1] == str(user) and i[-3] == None and i[-1] !='T'] #予約
    reserved_list += tori_list
    reserved_list2 = [i[2:-2] for i in all_reservation2 if i[1] == str(user) and i[-3] != None] #貸出し
    for i in reserved_list2:
        i.append('-') 
    tori_list2 = [i[2:-1] for i in all_reservation2 if i[1] == str(user) and i[-1] == 'T'] #取り置き
    for i in tori_list2:
        i.pop(-2)
        i.append(0) 
    borrow_list2 = [i[2:-3]  for i in all_reservation2 if i[1] == str(user) and i[-3] == None and i[-1] !='T'] #予約
    for i in borrow_list2:
        i.append("-") 
        i.append(1) 
    
    book_list = reserved_list2 + tori_list2 + borrow_list2
    
    return reserved_list,borrow_list,book_list,result_list


def page(page,all_text_member,all_text,result_list):
    sort_order = int(all_text_member[-1][-1]) #['ﾊﾟｲｿﾝ', '5', '21', '19', '<Page 1 of 2>4'] ⇒ 4
    print('---sort_order----',sort_order)
    if sort_order ==5:
        sortsecond = lambda val: val[sort_order]
        #print('---sort----',sortsecond)
        result_list.sort(reverse=True,key=sortsecond)
    elif sort_order==2:
        sortsecond = lambda val: val[sort_order]
        #print('---sort----',sortsecond)
        result_list.sort(reverse=True,key=sortsecond)
    elif sort_order==3:
        sort_order -= 1
        sortsecond = lambda val: val[sort_order]
        #print('---sort----',sortsecond)
        result_list.sort(key=sortsecond)
        sort_order += 1
    else:
        sort_order += 1
        sortsecond = lambda val: val[sort_order]
        #print('---sort----',sortsecond)
        result_list.sort(key=sortsecond)   
        sort_order -= 1  
    #----  ページネーション------------------------------------------------------------------
    page_document = all_text.split('|')[-1]
    page_number = page_document[page_document.find('page')+7:page_document.find('of')-1]
    job_paginator = Paginator(result_list,4)
    #page = self.request.GET.get('page')#, page_number)
    try:
        jobs = job_paginator.page(page)
        #print('----ook0---',jobs)
    except PageNotAnInteger:
        if len(all_text.split('%')) > 1:
            jobs = job_paginator.page(all_text.split('%')[-1].split(' ')[1])
            #print('----ook1---',jobs)
        elif "Page" in all_text.split('|')[-1]:
            jobs = job_paginator.page(all_text.split('|')[-1].split(' ')[1])
            #print('----ook2---',jobs)
        else:
            jobs = job_paginator.page(1)
            #print('----ook3---',jobs)
    except EmptyPage:
        jobs = job_paginator.page(1)
        #print('----ook4---',jobs)
    return jobs,sort_order