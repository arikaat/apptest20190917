from django.db import models
from django.utils.translation import ugettext_lazy as _     #多言語対応？

# Create your models here.


#変換するfileのmodel
class DataFile(models.Model):
    name = models.CharField(_('file name'), max_length=255,  blank=True)
    upfile = models.FileField(upload_to='test/',  verbose_name='upload file')
    dragarea = models.TextField(_('convert files'), blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('ファイル/File')
        verbose_name_plural = _('ファイル/File')