from django.views.generic import ListView,TemplateView,RedirectView,CreateView,DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin,UserPassesTestMixin
from django.contrib.auth import login,logout,authenticate,views as auth_views
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from pure_pagination.mixins import PaginationMixin
from .models import PublisherModel,AuthorModel,LibraryModel,BookModel,CustomUser,ReservationModel,HistoryModel,CommentModel
from .forms import LoginForm
import paginator
import mojimoji
import datetime
import jaconv
import MeCab
from django.core.cache import cache
import math
from django.db.models.functions import Concat
from django.db.models import Func

### 図書のメイン画面で、書籍の検索を可能とする。地図、情報、暦を表示する。
class MainView(TemplateView):
    template_name = 'main.html'
    model = CommentModel
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # cache削除
        key = "123"
        cache.delete(key)
        # commentModelに記載の情報をメイン画面に表示。
        comment_queryset = CommentModel.objects.all()
        comment_data = [[i.comment.replace('\\n','\n'),i.status] for i in comment_queryset]
        context['comment_data'] = comment_data
        return context
    def post(self,request,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # かんたん検索の入力文字に、'|<Page 1 of 1>2?'を加え検索結果(result）へ。ﾍﾟｰｼﾞﾈｰｼｮﾝの画面遷移と合わせるため。
        kensaku = request.POST['kantan']
        kensaku = kensaku + '|<Page 1 of 1>2?'
        # 未入力の場合、メインに戻す。
        if kensaku == '|<Page 1 of 1>2?' :
            return redirect('main')
        return redirect('result',kensaku)


### 検索結果を表示する。予約の仮選択(ﾎﾝﾁｬﾝはﾏｲﾍﾟｰｼﾞで)、予約・貸出書籍の確認、予約書籍のｷｬﾝｾﾙができる。
class ResultView(PaginationMixin,TemplateView):
    model = BookModel
    template_name = 'result.html'   
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # メイン画面のかんたん検索の入力文字を取得。最後の"?"を除く。
        all_text = self.kwargs['kensaku'][:-1] # ﾊﾟｲｿﾝ|5|21|19|<Page 1 of 2>4　(?を除去)
        all_text_member =  all_text.split('|') # ['ﾊﾟｲｿﾝ', '5', '21', '19', '<Page 1 of 2>4']
        key_word = all_text_member[0]          # ﾊﾟｲｿﾝ

        # MeCabによる形態素解析------------------------------------------------------------------
        key_word = key_word.replace("","") # 半角ｽﾍﾟｰｽ削除
        mecab = MeCab.Tagger("unidic")
        word_list = mecab.parse(key_word).split("\n")
        keyword = []
        for i in word_list:
            if ("助詞" not in i)and("EOS" not in i)and("補助記号" not in i):
                keyword.append(i.split('\t')[0])

        # MeCabの形態素解析の結果を、「ひらがな ⇒ カタカナ ⇒ 半角(ｶﾀｶﾅ)」に変換。-----------------
        #   ※BookModelのｷｰﾜｰﾄﾞ(book3)を半角の英数、ｶﾅとする。
        keyword_list = []
        for i in keyword:        
            kword = jaconv.hira2hkata(i)       # ひらがな⇒カタカナ
            kword = mojimoji.zen_to_han(kword) # 全角⇒半角
            kword = kword.lower()              # 大文字⇒小文字
            keyword_list.append(kword)
        
        # キャッシュ-----------------------------------------------------------------------------
        key = "123"
        data = cache.get(key)
        #cacheにdataがない、または、保存したkeyword_listが異なる場合は、再度クエリを発行。
        class ConcatOp(Func):
            function = ""
            arg_joiner = " || "
        if not data or data[0] != keyword_list:
            if len(keyword_list)==1:
                 result = []
            else:
                for i in range(len(keyword_list)):# 整形したｷｰﾜｰﾄﾞ(keyword_list)でfilterし、検索。
                    if i==0:
                        result = BookModel.objects.annotate(search=ConcatOp("book2","publisher__publisher2","author__author2")).filter(search__icontains=keyword_list[i])
                        #result = BookModel.objects.annotate(search=Concat("book2","publisher__publisher2","author__author2")).filter(search__icontains=keyword_list[i])
                        result = result.filter(search__icontains=keyword_list[i]).select_related('author').select_related('publisher')
                    else:
                        result = result.filter(search__icontains=keyword_list[i]).select_related('author').select_related('publisher')
                # userを設定。
                if self.request.user.is_anonymous:
                    user = 0
                else:
                    user = self.request.user
            """  テーブルデータ不正により、book3の使用を停止。
                for i in range(len(keyword_list)):# 整形したｷｰﾜｰﾄﾞ(keyword_list)でfilterし、検索。
                    if i==0:
                        result = BookModel.objects.filter(book3__icontains=keyword_list[i])
                        result = result.filter(book3__icontains=keyword_list[i]).select_related('author').select_related('publisher')
                    else:
                        result = result.filter(book3__icontains=keyword_list[i]).select_related('author').select_related('publisher')
                # userを設定。
                if self.request.user.is_anonymous:
                    user = 0
                else:
                    user = self.request.user
            """
      
            #　クエリ発行--------------------
            reserved_list,borrow_list,book_list,result_list = paginator.pagination(result,user)
            #　結果をchacheに保存------------
            test = []
            for i in keyword_list,reserved_list,borrow_list,result_list,book_list:
                test.append(i)
            cache.set(key,test,60*10)
        # cacheデータを使用------------------
        elif data[0] == keyword_list:
            reserved_list = data[1]
            borrow_list = data[2]
            result_list = data[3]
            book_list = data[4]

        # ソート -------------------------------------------------------------------------------
        # kensau　の　<Page * of *> を、修正。　ﾊﾟｲｿﾝ|5|21|19|<Page 1 of 2>4　-->　ﾊﾟｲｿﾝ|5|21|19|<Page 2 of 6>4
        page = self.request.GET.get('page')
        c_position = all_text.find('|<Page') + 7
        if page==None:
            page = all_text[c_position]
        f_calcture = all_text[:c_position] + str(page) + ' of ' + str(math.ceil((len(result_list)/4))) + '>' + all_text[-1]
        all_text = f_calcture
        jobs,sort_order = paginator.page(page,all_text_member,all_text,result_list)

        # context作成---------------------------------------------------------------------------
        kensaku = '|'.join(all_text.split('|')[:-1]) # ﾊﾟｲｿﾝ|5|21|19|<Page 1 of 2>4 ⇒　ﾊﾟｲｿﾝ|5|21|19
        if kensaku == "":
            kensaku = all_text
        print('--all_text_m---',[int(i) for i in all_text_member[1:-1]])
        context['num'] = [int(i) for i in all_text_member[1:-1]] #予約の仮選択した書籍のNo.。　ﾏｲﾍﾟｰｼﾞにて正式に予約手続き。
        context['jobs'] = jobs                   #ﾍﾟｰｼﾞﾈｰｼｮﾝのﾍﾟｰｼﾞ番号　 <Page 1 of 6>
        context['sort_order'] = sort_order       #sort_order:ｿｰﾄ種類
        context['kensaku'] = kensaku             # かんたん検索の入力文字
        context['reserved_list'] = reserved_list #予約済の書籍No.
        context['borrow_list'] = borrow_list     #貸出中の書籍No.
        context['book_list'] = book_list         #予約&貸出中の書籍ﾃﾞｰﾀ
        return context
    
    def post(self,request,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # 選択ボタンの検出 ------------------------------------
        try:
            choice = request.POST['choice']          # 検索文字、予約の仮選択した書籍No.、ページ情報。例：python|5+17+<Page 2 of 6>2?
            orignal = choice.split('+')              # choiceを"+"で分割し、orignalへ。
            original_marge = '|'.join(orignal)       # choiceの記載を変換。　例：python|5|17|<Page 2 of 6>2?
            all_items = []                           # all_items ：選択のする・しないを繰り返した際の、重複を排除。
            item_l = original_marge.split('|')[1:-1] # 予約の仮選択した書籍No.のﾘｽﾄ　例：['5', '17']
            # all_items ：選択のする・しないを繰り返した際の、重複を排除。
            for i in item_l:
                if i not in all_items:
                    all_items.append(i)
                else:
                    all_items.remove(i)
            # kensakuの作成。
            if all_items == []:
                kensaku = orignal[0].split('|')[0] + '|' + orignal[2] #kensaku = orignal[0]
            else:
                kensaku = orignal[0].split('|')[0] + '|' + '|'.join(all_items) + '|'+ orignal[2]
            context['kensaku'] = kensaku
            return redirect('result',kensaku)
        except:
            print('---no_choice----')
        # 登録ボタンの検出 ------------------------------------
        try:
            reservation = self.request.POST['reservation']
            if reservation.find('|') > 0 :
                reservation += '|<Page 1 of 1>2' #ﾍﾟｰｼﾞﾈｰｼｮﾝの画面遷移と合わせるため、'|<Page 1 of 1>2?'を追加。
                return redirect('reservation',reservation)
            else:
                reservation += '|<Page 1 of 1>2' #ﾍﾟｰｼﾞﾈｰｼｮﾝの画面遷移と合わせるため、'|<Page 1 of 1>2?'を追加。
                return redirect('reservation',reservation)
                #return redirect('main')
        except:
            print('---no_reserve---')
        # Prevボタンの検出------------------------------------
        try:
            prev = request.POST['prev'] #ソートボタンの検出
            # prevからの"&&"を削除。
            kensaku = prev.split('&&')[0] + prev.split('&&')[1] + '?' # 例：python|5|17|<Page 1 of 2>4?
        except:
            print('---no_prev---')
        # cancelの検出 -----------------------------------------
        try:
            cancel = request.POST['cancel'] #キャンセルボタンの検出
            print('---cancel---',cancel)
            cancel_list = cancel.split('+')
            book = ReservationModel.objects.get(user=self.request.user,book__book=cancel_list[1])
            book.delete()
            kensaku = cancel_list[0] + " " + cancel_list[0][0] + '|' + cancel_list[-1] + "?"#'|<Page 1 of 1>2?'
            other_reservation = ReservationModel.objects.filter(book__book=cancel_list[1])
            print('---kensaku2--',kensaku)
        except:
            print('---no_cancel---')
        #------------------------------------------------------
        return redirect('result',kensaku)


### マイページ画面(reservation)の表示。予約ができる。予約・貸出書籍（自・他）の確認、また、予約書籍のｷｬﾝｾﾙができる。
class ReservationView(LoginRequiredMixin,TemplateView):
    template_name = 'reservation.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        all_text = self.kwargs['reservation']     # ﾊﾟｲｿﾝ|5|21|19|4|1|2%5%21%<Page 1 of 2>2
        all_text_member = all_text.split('%')     # ['ﾊﾟｲｿﾝ|5|21|19|4|1|2', '5', '21', '<Page 1 of 2>2']
        num = all_text_member[0].split('|')[1:]   # ['5', '21', '19', '4', '1', '2' , '<Page 1 of 2>4']
        num =[int(i) for i in num if i.isdigit()] # [5, 21, 19, 4, 1, 2]　予約の仮選択No.のリスト（isdigitで、文字列が数値のみ）
        result = []
        for book in num:
            result += BookModel.objects.filter(id=book)
        # ソートの種類を取得。
        sort_order = int(all_text_member[-1][-1]) # ['ﾊﾟｲｿﾝ|5|21|19|4|1|2', '5', '21', '<Page 1 of 2>2'] --> 2
        # 現在のページを取得。

        # ﾍﾟｰｼﾞﾈｰｼｮﾝ ---------------------------------------------------------------------------
        user=self.request.user
        reserved_list,borrow_list,book_list,result_list = paginator.pagination(result,user)
        # kensau　の　<Page * of *> を、修正。　ﾊﾟｲｿﾝ|5|21|19|<Page 1 of 2>4　-->　ﾊﾟｲｿﾝ|5|21|19|<Page 2 of 6>4
        page = self.request.GET.get('page')
        c_position = all_text.find('<Page') + 6
        if page==None:
            page = all_text[c_position]
        f_calcture = all_text[:c_position] + str(page) + ' of ' + str(math.ceil(len(result_list)/4)) + '>' + all_text[-1]
        all_text = f_calcture
        jobs,sort_order = paginator.page(page,all_text_member,all_text,result_list)

        # ソート-----------
        try:
            all_text_member_int = [int(i) for i in all_text_member[1:-1] if i!="" ] #['ﾊﾟｲｿﾝ|5|21|19|4|1|2', '5', '21', '<Page 1 of 2>2'] --> [5,21]            
            for i in all_text_member_int:
                if i in num:
                    num.remove(i)
                else:
                    num.append(i)
        except:
            print('---ng---')
        if '%' not in all_text:
            delete_book = []
            for i in borrow_list:
                if i in num:
                    delete_book.append(str(i))
            for i in reserved_list:
                if i in num:
                    delete_book.append(str(i))
            delete_b = '%'.join(delete_book)
            all_text2 = all_text.split('<')
            all_text = all_text2[0] + '%' + delete_b + '%<' + all_text2[1]

        #----  context作成----------------------------------------------------
        context['num'] = num                     #予約の仮選択した書籍のNo.。　ﾏｲﾍﾟｰｼﾞにて正式に予約手続き。
        context['jobs'] = jobs                   #ﾍﾟｰｼﾞﾈｰｼｮﾝのﾍﾟｰｼﾞ番号　 <Page 1 of 6>
        context['sort_order'] = sort_order       #sort_order:ｿｰﾄ種類
        context['kensaku'] = all_text            # かんたん検索の入力文字
        context['reserved_list'] = reserved_list #予約済の書籍No.
        context['borrow_list'] = borrow_list     #貸出中の書籍No
        context['book_list'] = book_list         #予約&貸出中の書籍ﾃﾞｰﾀ
        return context
    
    def post(self,request,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        # 選択ボタンの検出 ---------------------------------------------
        try:
            orignal = (request.POST['choice']).split('+')
            orignal_first = orignal[0].split('<')[0]
            if orignal_first[-1] != '%':
                orignal_first += '%'
            kensaku = orignal_first + orignal[1] + '%' + orignal[2]
            context['kensaku'] = kensaku
            return redirect('reservation',kensaku)
        except:
            print('---R_no_choice---')
        # 登録ボタンの検出 ----------------------------------------------
        try:
            reservation = request.POST['reservation']      #ﾊﾟｲｿﾝ|5|21|19|4|1|2%5%21%<Page 1 of 2>2
            reservation_list = reservation.split('|')[1:-1]#[5,21,19,4,1]
            non_reservation = reservation.split('%')[1:-1] #[5,21]
            for i in non_reservation:
                if i in reservation_list:
                    reservation_list.remove(i)             #[19,4,1]  5,21,  [21,19,4,1]  5,   
                else:
                    if i != "":
                        reservation_list.append(i)         #もし　non-resが[5,21､5]なら　5　復活
            for i in reservation_list:                     #[19,4,1]
                res_book = BookModel.objects.get(id =i)
                today = datetime.date.today()              #status=1がなければ、他に予約はなく、status=1で登録
                reservation_number = ReservationModel.objects.filter(book=res_book,status="1").count()
                if reservation_number==0:
                    ReservationModel.objects.create(book=res_book,reservation_date=today,user=self.request.user,status=1)
                else:
                    ReservationModel.objects.create(book=res_book,reservation_date=today,user=self.request.user)
            return redirect('logout')
        except:
            print('---R_no_reserve---')
        # Prevボタンの検出 --------------------------------------------
        try:
            prev = request.POST['prev']
            kensaku = prev.split('&&')[0]
            kensaku_part = kensaku.split('<')
            if len(kensaku_part) > 2:
                kensaku = kensaku_part[0]+ '<' + kensaku_part[-1] + prev.split('&&')[1]
        except:
            print('---R_no_prev----')
            sort_order = 2
        # キャンセルボタンの検出 ---------------------------------------
        try:
            cancel = request.POST['cancel']
            cancel = cancel.split('+')
            # キャンセルされた本の予約総数
            reservation_number = ReservationModel.objects.filter(book__book=cancel[1]).count()
            # キャンセルされた本は取置き本、また、取置き数
            reserving_book = ReservationModel.objects.filter(book__book=cancel[1],status="T") ### 取り置き本（0か1）
            reserving_book = [i.id for i in reserving_book]
            reserving_book_number = len(reserving_book)
            # キャンセルされた本は貸出しているか、また、その総数（0か1）
            rented_book = ReservationModel.objects.filter(book__book=cancel[1],start_date__gt="2000-01-01") ### その本の貸出している書籍
            rented_book = [i.id for i in rented_book]
            rented_number = len(rented_book)
            book = ReservationModel.objects.get(user=self.request.user,book__book=cancel[1])
            book.delete()
            kensaku = cancel[0]
            if reservation_number - reserving_book_number - rented_number > 1 :
                reserving = ReservationModel.objects.filter(book__book=cancel[1])
                reserving_list = [i.id for i in reserving if i.id not in rented_book]
                reserving_list = [i.id for i in reserving if i.id not in reserving_book]
                reserving_list.sort()
                book = ReservationModel.objects.get(id=reserving_list[0],book__book=cancel[1])
                book.status = 1
                book.save()
            else:
                print('nothing')
        except:
            print('---R_no-cancel---')
        return redirect('reservation',kensaku)#,sort_order) 

### メインに表示する情報　----------------------------------------------
class InformationView(TemplateView):
    template_name = 'information.html'

### 過去の貸出し履歴を表示 ---------------------------------------------
class HistoryView(ListView):
    template_name = 'history.html'
    model = HistoryModel
    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        kensaku = self.kwargs['kensaku']
        object_list = HistoryModel.objects.filter(user=self.request.user)
        context['kensaku'] = kensaku
        context['object_list'] = object_list
        return context 
    
### Login -----------------------------------------------------------
class LoginView(auth_views.LoginView):
    template_name='login.html'
    form_class = LoginForm

### Logout ----------------------------------------------------------
class LogoutView(LoginRequiredMixin,LogoutView):
    template_name= 'logout.html'