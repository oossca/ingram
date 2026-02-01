"""命令行参数"""
import argparse


def get_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in_file', type=str, required=True, help='the targets will be scan')
    parser.add_argument('-o', '--out_dir', type=str, required=True, help='the dir where results will be saved')
    parser.add_argument('-p', '--ports', type=int, nargs='+', default=None, help='the port(s) to detect')
    parser.add_argument('-t', '--th_num', type=int, default=150, help='the processes num')
    parser.add_argument('-T', '--timeout', type=int, default=3, help='requests timeout')
    parser.add_argument('-D', '--disable_snapshot', action='store_true', help='disable snapshot')
    parser.add_argument('--debug', action='store_true', help='log all msg')
    parser.add_argument('-u', '--users_file', type=str, default=None, help='file containing usernames list')
    parser.add_argument('-P', '--passwords_file', type=str, default=None, help='file containing passwords list')
    
    # FOFA相关参数
    parser.add_argument('--fofa_email', type=str, default=None, help='FOFA account email')
    parser.add_argument('--fofa_key', type=str, default=None, help='FOFA API key')
    parser.add_argument('--fofa_query', type=str, default='camera', help='FOFA search query (default: camera)')
    parser.add_argument('--fofa_max', type=int, default=1000, help='Maximum FOFA results (default: 1000)')
    parser.add_argument('--use_fofa', action='store_true', help='Use FOFA to get targets instead of input file')

    args = parser.parse_args()
    return args