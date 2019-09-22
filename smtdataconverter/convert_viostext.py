#convert本体。
#yamahaのVIOS-TEXTを変換する。
from django.shortcuts import render
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.views import generic
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, resolve_url
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from weakref import WeakValueDictionary

import pandas as pd     #pandas pip install が必要
import numpy as np      #numpy pip install が必要

from .forms import ConvertForm, FileUploadForm
from accounts import views as accountsviews
from .models import DataFile


import csv
import io
import sys

#file convert main






