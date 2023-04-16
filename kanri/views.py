from django.views.generic import ListView,TemplateView,RedirectView,CreateView,DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin,UserPassesTestMixin
from django.contrib.auth import login,logout,authenticate,views as auth_views
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from pure_pagination.mixins import PaginationMixin
from jobplace.models import BookModel,CustomUser,ReservationModel,HistoryModel,CommentModel
import paginator
import datetime


#################### 以下、管理者用 #######################################################
# 貸出し・返却:ユーザーを設定後、貸出し・返却を行なう。貸出しは5冊まで。
#             取置きが有る場合、返却する本に予約があり取置きが必要な場合を、管理者に知らせる。
class RentView(UserPassesTestMixin,TemplateView):
    template_name = 'rent.html'
    model = ReservationModel
    def test_func(self):
        return self.request.user.is_staff
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        try:
            userid = self.kwargs['userid']
            user = CustomUser.objects.get(username=userid)
            reserved_books = ReservationModel.objects.filter(user=user)
            reserved_books_list = [[i.book.book,i.book.author.author,i.book.publisher.publisher,\
                i.limited_date,i.end_date] for i in reserved_books]
            for i in reserved_books_list:
                res = ReservationModel.objects.filter(user=user,book__book=i[0],start_date__gt="2000-01-01")
                res_list = [i.book for i in res]
                for j in res_list:
                    if ReservationModel.objects.filter(book__book=j).count() > 1:
                        i[3] = "t"
            rent_book = ReservationModel.objects.filter(user=user,start_date__gt="2000-01-01")
            rent_book = [i.book.book for i in rent_book]
            context["book_list"] = reserved_books_list
            context["userid"] = userid
            context["rent_book"] = rent_book
            return context
        except:
            print('---Rent_ng---')
            return
    def post(self,request,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザ設定：ユーザIDを入力し、対象者を決める#####
        try:
            userid = request.POST['userid']
            return redirect('rent',userid)
        except:
            print('--Rent_ng_userid--')
        # 貸出し・返却　---------------------------------
        try:
            rent_book = request.POST['book']
            userid = request.POST['reservation']
            user = CustomUser.objects.get(username=userid)
            rent_book_number = ReservationModel.objects.filter(user=user,start_date__gt="2000-01-01").count()#貸出している書籍の数
            rented_book_number = ReservationModel.objects.filter(book__book=rent_book,start_date__gt="2000-01-01").count()#書籍の貸出し数（1か0）
            reserving_book_number = ReservationModel.objects.filter(user=user,book__book=rent_book,status="T").count()
            today = datetime.date.today()
            day_after_tomorrow = datetime.timedelta(days=14)
            end_day = today + day_after_tomorrow
            rented_book = BookModel.objects.get(book=rent_book)
            # 返却：貸出し書籍の数=１。　貸出していた本、つまり返却。予約から削除し、履歴に移動。
            if  rented_book_number == 1:
                rented_book = ReservationModel.objects.get(book=rented_book ,user=user)
                rented_book.delete()
                book = HistoryModel.objects.create(book=rented_book , start_day=rented_book.start_date, end_day=rented_book.end_date, user=user)
            # 貸出し(取り置きしたいた本)　取り置き期限、status=T を削除。#
            elif rent_book_number < 5 and reserving_book_number == 1:
                book = ReservationModel.objects.get(book=rented_book ,user=user)
                book.start_date = today
                book.end_date = end_day
                book.limited_date = None
                book.status = None
                book.save()
            # 貸出し ------------------------------------
            #　 予約をしたが、直ぐに図書館の書棚の本を持って、受付で予約する場合。(予約を削除)                                           ######
            #　 同じユーザは、特定の本の予約は、１つしかできない。（既に予約がある本は、マイページでボタンが【予約済】となり予約ができない）######
            #　 取置き済みの本を、他のユーザが受付で貸出しはできない。                                                                  ######
            elif rent_book_number < 5 and  rented_book_number == 0:
                try:
                    rent_book = BookModel.objects.get(book=rent_book)
                    reserved_book = ReservationModel.objects.get(book=rent_book,user=user)
                    reserved_book.delete()
                except:
                    print('ng2')
                rent_book = BookModel.objects.get(book=rent_book)
                book = ReservationModel.objects.create(book=rent_book,start_date=today,end_date=end_day,user=user)
                return redirect('rent',userid)
        except:
            print('--ng--')
        return redirect('rent',userid)

### 予約本の取置き：取り置きの対象、取り置き期限切れを管理者に知らせる。
class ReservingView(UserPassesTestMixin,TemplateView):
    template_name = 'reserving.html'
    model = ReservationModel
    def test_func(self):
        return self.request.user.is_staff
    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # 貸出している本 
        borrowed_book = ReservationModel.objects.filter(start_date__gt="2000-01-01")
        borrowed_books = [i.book.book for i in borrowed_book]  
        # 取置き済みの本 
        reserved_book = ReservationModel.objects.filter(status='T') 
        reserved_books = [i.book.book for i in reserved_book] 
        # 貸出しや取置き済みの本。reserving_list作成のためにまとめる。 
        borrowed_reserved_books = borrowed_books + reserved_books 
        # 取置きの対象：貸出しや取置きをしていない、取置きのstatusが"1"のリスト。 
        reserving = ReservationModel.objects.filter(status="1")
        reserving_list = [[i.book.book,i.book.author.author,i.book.publisher.publisher,\
            i.book.year,i.user.username,0] for i in reserving if i.book.book not in borrowed_reserved_books]
        context["book_list"] = reserving_list 
        # 取置き済み本：取置き期限が切れキャンセル対象となる予約を管理者に知らせる 
        reserved = ReservationModel.objects.filter(status="T")
        reserved_list = [[i.book.book,i.book.author.author,i.book.publisher.publisher,\
            i.limited_date,i.user.username,0] for i in reserved ]
        context["reserved_list"] = reserved_list
        return context
    def post(self,request,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # 管理者は、取り置き対象の本を、書棚から持ち帰った際、取置きボタンにて、取置きを行なう。
        # 取置き後は、予約データのstatusを"T"、取り置き期限を1週間後、変更する。
        # また、他に予約があれば、最も速い予約(idが小さい）のstatusを"1"に、変更する。（sort後、[0]を対象にする)
        try:
            implement = request.POST['implement']
            book = ReservationModel.objects.get(book__book=implement,status=1)
            book.status = "T" ###"T"は取置き済みを示す。
            today = datetime.date.today()
            limited_day = datetime.timedelta(days=7)
            book.limited_date = today + limited_day
            book.save()
            # 他予約があれば、最も速い予約のstausを"1"に変更 
            other_book = ReservationModel.objects.filter(book__book=implement)
            other_book = [i.id for i in other_book if i.id != book.id]
            other_book.sort()
            if len(other_book)>0:
                book = ReservationModel.objects.get(id=other_book[0])
                book.status = "1" #　"1"は、最も速い予約を示す。
                book.save()
            return redirect('reserving')
        except:
            print('ng')
        # 取置き期限切れの予約を削除する。 その際、他に予約があれば、最も速い予約のstatusを"1"に変更する。      
        try:
            cancel = request.POST['cancel']
            book = ReservationModel.objects.get(book__book=cancel,status="T")
            book.delete()
            # 対象の全予約他→に予約があれば、最も速い予約のstatusを"1"に変更する 
            other_book = ReservationModel.objects.filter(book__book=cancel)
            other_book = [i.id for i in other_book if i.id != book.id]
            other_book.sort()
            if len(other_book)>0:
                book = ReservationModel.objects.get(id=other_book[0])
                book.status = "1"
                book.save()
            return redirect('reserving')
        except:
            print('ng')

### メインで表示する情報の一覧 
class CommentView(UserPassesTestMixin,ListView):
    model = CommentModel
    template_name = 'comment.html'
    def test_func(self):
        return self.request.user.is_staff
    
### メインで表示する情報の一覧の作成 
class CreateView(UserPassesTestMixin,CreateView):
    template_name = 'create.html'
    model =  CommentModel
    fields = ['comment','status']
    success_url = reverse_lazy('comment')
    def test_func(self):
        return self.request.user.is_staff
    
### メインで表示する情報の一覧の編集 
class UpdateView(UserPassesTestMixin,UpdateView):
    template_name = 'update.html'
    model = CommentModel
    fields = ['comment','status']
    success_url = reverse_lazy('comment')
    def test_func(self):
        return self.request.user.is_staff
    
### メインで表示する情報の一覧の削除 
class DeleteView(UserPassesTestMixin,DeleteView):
    template_name = 'delete.html'
    model = CommentModel
    success_url = reverse_lazy('comment') 
    def test_func(self):
        return self.request.user.is_staff