#! /usr/bin/env python3
# coding  : utf-8
# @Author : Jor<jorhelp@qq.com>
# @Date   : Wed Apr 20 00:17:30 HKT 2022
# @Desc   : Webcam vulnerability scanning tool

#=================== 需放置于最开头 ====================
import warnings; warnings.filterwarnings("ignore")
from gevent import monkey; monkey.patch_all(thread=False)
#======================================================

import os
import sys
from multiprocessing import Process

from loguru import logger

from Ingram import get_config
from Ingram import Core
from Ingram.utils import color
from Ingram.utils import common
from Ingram.utils import get_parse
from Ingram.utils import log
from Ingram.utils import logo
from Ingram.utils import fofa


def run():
    try:
        # logo
        for icon, font in zip(*logo):
            print(f"{color.yellow(icon, 'bright')}  {color.magenta(font, 'bright')}")

        # config
        config = get_config(get_parse())
        
        # 处理FOFA模式
        if config.use_fofa:
            if not config.fofa_email or not config.fofa_key:
                print(f"{color.red('FOFA mode requires email and API key!')}")
                print(f"{color.yellow('Use --fofa_email and --fofa_key parameters')}")
                sys.exit()
            
            # 从FOFA获取目标
            print(f"{color.cyan('正在从FOFA获取目标...')}")
            fofa_file = os.path.join(config.out_dir, "fofa_targets.txt")
            
            if not fofa.create_fofa_targets(
                config.fofa_email, 
                config.fofa_key, 
                config.fofa_query, 
                fofa_file, 
                config.fofa_max
            ):
                # 修改config的in_file为FOFA生成的文件
                config = config._replace(in_file=fofa_file)
                print(f"{color.green(f'FOFA目标已保存到: {fofa_file}')}")
            else:
                print(f"{color.red('FOFA获取目标失败!')}")
                sys.exit()
        
        if not os.path.isdir(config.out_dir):
            os.mkdir(config.out_dir)
            os.mkdir(os.path.join(config.out_dir, config.snapshots))
        if not os.path.isfile(config.in_file):
            print(f"{color.red('the input file')} {color.yellow(config.in_file)} {color.red('does not exists!')}")
            sys.exit()

        # log 配置
        log.config_logger(os.path.join(config.out_dir, config.log), config.debug)

        # 任务进程
        p = Process(target=Core(config).run)
        if common.os_check() == 'windows':
            p.run()
        else:
            p.start()
            p.join()

    except KeyboardInterrupt:
        logger.warning('Ctrl + c was pressed')
        if p.is_alive():
            p.terminate()
            p.join(timeout=5)
            if p.is_alive():
                p.kill()
        sys.exit()

    except Exception as e:
        logger.error(e)
        print(f"{color.red('error occurred, see the')} {color.yellow(config.log)} "
              f"{color.red('for more information.')}")
        if p.is_alive():
            p.terminate()
            p.join(timeout=5)
        sys.exit()


if __name__ == '__main__':
    run()
