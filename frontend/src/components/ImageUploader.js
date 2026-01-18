import React, { useState, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { toast } from 'sonner';
import axios from 'axios';
import { API_URL } from '../utils/api';
import { Upload, X, Image as ImageIcon, Link, Loader2 } from 'lucide-react';

const API = API_URL;

export default function ImageUploader({
  value,
  onChange,
  type = 'product', // product, category, general
  label = 'الصورة',
  placeholder = 'أدخل رابط الصورة أو ارفع صورة من جهازك',
  showPreview = true,
  className = ''
}) {
  const [uploading, setUploading] = useState(false);
  const [useUrl, setUseUrl] = useState(!value || value.startsWith('http'));
  const fileInputRef = useRef(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // التحقق من أن الملف صورة
    if (!file.type.startsWith('image/')) {
      toast.error('يرجى اختيار ملف صورة');
      return;
    }

    // التحقق من حجم الملف (أقصى 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('حجم الصورة يجب أن يكون أقل من 10 ميجابايت');
      return;
    }

    setUploading(true);
    
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response = await axios.post(`${API}/upload/image`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.image_url) {
        onChange(response.data.image_url);
        toast.success('تم رفع الصورة بنجاح');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'فشل في رفع الصورة');
    } finally {
      setUploading(false);
      // إعادة تعيين input الملف
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUrlChange = (e) => {
    onChange(e.target.value);
  };

  const handleClear = () => {
    onChange('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getFullImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    // إذا كان الرابط نسبي، نضيف له الـ base URL
    const baseUrl = window.location.origin;
    return `${baseUrl}${url}`;
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <Label className="text-foreground">{label}</Label>
      
      {/* أزرار التبديل */}
      <div className="flex gap-2 mb-2">
        <Button
          type="button"
          variant={useUrl ? "default" : "outline"}
          size="sm"
          onClick={() => setUseUrl(true)}
          className="flex items-center gap-1"
        >
          <Link className="h-3 w-3" />
          رابط
        </Button>
        <Button
          type="button"
          variant={!useUrl ? "default" : "outline"}
          size="sm"
          onClick={() => setUseUrl(false)}
          className="flex items-center gap-1"
        >
          <Upload className="h-3 w-3" />
          رفع صورة
        </Button>
      </div>

      {useUrl ? (
        /* إدخال رابط */
        <div className="flex gap-2">
          <Input
            type="url"
            value={value || ''}
            onChange={handleUrlChange}
            placeholder={placeholder}
            className="flex-1"
          />
          {value && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={handleClear}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      ) : (
        /* رفع ملف */
        <div className="space-y-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id={`image-upload-${type}`}
          />
          
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex-1"
            >
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 ml-2 animate-spin" />
                  جاري الرفع...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 ml-2" />
                  اختر صورة من الجهاز
                </>
              )}
            </Button>
            {value && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={handleClear}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          
          <p className="text-xs text-muted-foreground">
            الصيغ المدعومة: JPG, PNG, GIF, WEBP, HEIC, BMP, TIFF (أقصى 10MB)
          </p>
        </div>
      )}

      {/* معاينة الصورة */}
      {showPreview && value && (
        <div className="mt-3">
          <div className="relative w-24 h-24 rounded-lg border overflow-hidden bg-muted">
            <img
              src={getFullImageUrl(value)}
              alt="معاينة"
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
            <div className="hidden absolute inset-0 items-center justify-center bg-muted">
              <ImageIcon className="h-8 w-8 text-muted-foreground" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
