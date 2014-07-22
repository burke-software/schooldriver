from django.contrib import admin

from ecwsp.omr.models import *

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    
class AnswerBankInline(admin.TabularInline):
    model = AnswerBank
    extra = 4
    
class AnswerInstanceInline(admin.TabularInline):
    model = AnswerInstance
    extra = 0

admin.site.register(NetworkQuestionBank)

class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'link_copy']
    
admin.site.register(Test, TestAdmin)

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]    
admin.site.register(Question, QuestionAdmin)

class AnswerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Answer, AnswerAdmin)

class TestInstanceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'points_possible', 'points_earned', 'grade']
    inlines = [AnswerInstanceInline]
admin.site.register(TestInstance, TestInstanceAdmin)

admin.site.register(AnswerInstance)

admin.site.register(AnswerBank, AnswerAdmin)

class QuestionBankAdmin(admin.ModelAdmin):
    inlines = [AnswerBankInline]    
admin.site.register(QuestionBank,QuestionBankAdmin)
