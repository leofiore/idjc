/*
#   dyn_lame.c: dynamic linking for LAME
#   Copyright (C) 2009 Stephen Fairchild (s-fairchild@users.sourceforge.net)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program in the file entitled COPYING.
#   If not, see <http://www.gnu.org/licenses/>.
*/

#include "../config.h"

#ifdef DYN_LAME

#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include "dyn_lame.h"
#include "lame.h"

static void *handle;

static lame_global_flags *(*init)();
static int (*encode_flush_nogap)(lame_global_flags *, unsigned char *, int);
static int (*set_num_channels)(lame_global_flags *, int);
static int (*set_brate)(lame_global_flags *, int);
static int (*set_in_samplerate)(lame_global_flags *, int);
static int (*set_out_samplerate)(lame_global_flags *, int);
static int (*set_mode)(lame_global_flags *, MPEG_mode);
static int (*set_quality)(lame_global_flags *, int);
static int (*set_free_format)(lame_global_flags *, int);
static int (*set_bWriteVbrTag)(lame_global_flags *, int);
static int (*init_params)(lame_global_flags *);
static int (*close)(lame_global_flags *);
static int (*encode_buffer_float)(lame_global_flags *,
                                        const float [],
                                        const float [],
                                        const int,
                                        unsigned char *,
                                        const int);

static void dyn_lame_close()
    {
    dlclose(handle);
    }

int dyn_lame_init()
    {
    char *error;

    if (!((handle = dlopen("libmp3lame.so", RTLD_LAZY)) ||
            (handle = dlopen("libmp3lame.dylib", RTLD_LAZY)) ||
            (handle = dlopen("liblame.so", RTLD_LAZY)) ||
            (handle = dlopen("liblame.dylib", RTLD_LAZY))))
        {
        fprintf(stderr, "failed to locate lib[mp3]lame dynamic library\n");
        return 0;
        }
    dlerror();

    if (!(   (init = dlsym(handle, "lame_init")) &&
                (encode_flush_nogap = dlsym(handle, "lame_encode_flush_nogap")) &&
                (set_num_channels = dlsym(handle, "lame_set_num_channels")) &&
                (set_brate = dlsym(handle, "lame_set_brate")) &&
                (set_in_samplerate = dlsym(handle, "lame_set_in_samplerate")) &&
                (set_out_samplerate = dlsym(handle, "lame_set_out_samplerate")) &&
                (set_mode = dlsym(handle, "lame_set_mode")) &&
                (set_quality = dlsym(handle, "lame_set_quality")) &&
                (set_free_format = dlsym(handle, "lame_set_free_format")) &&
                (set_bWriteVbrTag = dlsym(handle, "lame_set_bWriteVbrTag")) &&
                (init_params = dlsym(handle, "lame_init_params")) &&
                (close = dlsym(handle, "lame_close")) &&
                (encode_buffer_float = dlsym(handle, "lame_encode_buffer_float"))))
        {
        fprintf(stderr, "missing symbols in lib[mp3]lame\n");
        }

    if ((error = dlerror()))
        {
        fprintf(stderr, "dlsym failed with: %s\n", error);
        dlclose(handle);
        return 0;
        }

    atexit(dyn_lame_close);
    return 1;
    }

lame_global_flags *lame_init()
    {
    return init();
    }

int lame_encode_flush_nogap(lame_global_flags *gfp, unsigned char *mp3buf, int size)
    {
    return encode_flush_nogap(gfp, mp3buf, size);
    }

int lame_set_num_channels(lame_global_flags *gfp, int channels)
    {
    return set_num_channels(gfp, channels);
    }

int lame_set_brate(lame_global_flags *lgf, int brate)
    {
    return set_brate(lgf, brate);
    }

int lame_set_in_samplerate(lame_global_flags *lgf, int inrate)
    {
    return set_in_samplerate(lgf, inrate);
    }

int lame_set_out_samplerate(lame_global_flags *lgf, int outrate)
    {
    return set_out_samplerate(lgf, outrate);
    }

int lame_set_mode(lame_global_flags *lgf, MPEG_mode mode)
    {
    return set_mode(lgf, mode);
    }

int lame_set_quality(lame_global_flags *lgf, int quality)
    {
    return set_quality(lgf, quality);
    }

int lame_set_free_format(lame_global_flags *lgf, int free)
    {
    return set_free_format(lgf, free);
    }

int lame_set_bWriteVbrTag(lame_global_flags *lgf, int tag)
    {
    return set_bWriteVbrTag(lgf, tag);
    }

int lame_init_params(lame_global_flags *lgf)
    {
    return init_params(lgf);
    }

int lame_close(lame_global_flags *lgf)
    {
    return close(lgf);
    }

int lame_encode_buffer_float(lame_global_flags *lgf,
                                        const float buffer_l[],
                                        const float buffer_r[],
                                        const int   nsamples,
                                        unsigned char *mp3buf,
                                        const int      mp3buf_size)
    {
    return encode_buffer_float(lgf, buffer_l, buffer_r,
                                         nsamples, mp3buf, mp3buf_size);
    }

#endif /* DYN_LAME */
