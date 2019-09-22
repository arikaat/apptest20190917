#CustomUser管理用モデル。モデルはクラスに相当しこの内容でDBのテーブルが生成される。
#真っ先に定義するべきModel
#UserNameはE-MailAddressを使用する
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager

#20190819ここから追加/////////////////////////////////////////////////////////////////////////////////////////////
#工場名クラス
class Factory(models.Model):
    name = models.CharField(_('factory name'), max_length=255, blank=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('工場名/Factory Name')
        verbose_name_plural = _('工場名/Factory Name')

#部署名クラス
class Department(models.Model):
    name = models.CharField(_('department'), max_length=255, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('部署名/Deprtment')
        verbose_name_plural = _('部署名/Deprtment')

#役職クラス
class OfficialPosition(models.Model):
    name = models.CharField(_('official position'), max_length=255, blank=False)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('役職/Official Position')
        verbose_name_plural = _('役職/Official Position')

#20190823追加////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#電話番号クラス
class PhoneNumber(models.Model):
    _number = models.CharField(_('phone number'), max_length=50, blank=True)
    def __str__(self):
        return self._number
    
    class Meta:
        verbose_name = _('電話番号/Phone Number')
        verbose_name_plural = _('電話番号/Phone Number')
#20190823追加ここまで////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#初期値クラス
#会社名クラス。
class Company(models.Model):
    name = models.CharField(_('company name'), max_length=255,  blank=False)
    factoryname = models.ForeignKey(Factory, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    officialposition = models.ForeignKey(OfficialPosition, on_delete=models.CASCADE)
    phonenumber = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_factory(self):
        return self.factoryname.name

    def get_department(self):
        return self.department.name

    def get_officialposition(self):
        return self.officialposition.name

    def get_phonenumber(self):
        return self.phonenumber

    class Meta:
        verbose_name = _('会社名/Company Name')
        verbose_name_plural = _('会社名/Company Name')

#20190819　ここまで追加////////////////////////////////////////////////////////////////////////////////////////////

#CustumUser関連////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class UserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    #20190808下記追加
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name = _('会社名/Company Name'))

    #20190823ここから追加//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    #License関連
    membershiplicense = models.BooleanField(
        default=False, 
        verbose_name = _('メインライセンス/Membership License'),
        help_text=_(
            '会員ライセンスの本体'),
    )
    #20190823ここまで追加//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_company(self):
        return self.company.name

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email