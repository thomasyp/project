set nocompatible " 去掉vim的扩展，和vi保持兼容
" autoformat sets
syntax on
filetype plugin indent on
set ic
set hlsearch
set encoding=utf-8
set fileencodings=utf-8,ucs-bom,GB2312,big5
set cursorline
hi CursorLine   cterm=NONE ctermbg=LightCyan ctermfg=white guibg=darkred guifg=white
set autoindent
set smartindent
set scrolloff=4
set showmatch
set nu
set ignorecase
set foldmethod=indent
set foldlevel=99

set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" let Vundle manage Vundle, required 让Vundle管理Vundle
" All of your Plugins must be added before the following line
Plugin 'VundleVim/Vundle.vim'

Plugin 'altercation/vim-colors-solarized'
Plugin 'endel/vim-github-colorscheme'
" Awesome looking meta at bottom
" Fugitive will help with git related stuff, and show branch on statusline
Plugin 'tpope/vim-fugitive' 
Plugin 'vim-airline/vim-airline-themes'

Plugin 'Chiel92/vim-autoformat'
Plugin 'scrooloose/nerdtree'
Plugin 'kien/rainbow_parentheses.vim'
Plugin 'https://github.com/bling/vim-airline'
Plugin 'Lokaltog/vim-powerline'
Plugin 'vim-scripts/khaki.vim'

"powerline
set helplang=cn
" " 设置为双字宽显示，否则无法完整显示如:☆
set ambiwidth=double
" " 总是显示状态栏 
let laststatus = 2
" let g:airline_powerline_fonts = 1   " 使用powerline打过补丁的字体
" " 开启tabline
let g:airline#extensions#tabline#enabled = 1
" "tabline中当前buffer两端的分隔字符
let g:airline#extensions#tabline#left_sep = ' '
" "tabline中未激活buffer两端的分隔字符
" "tabline中buffer显示编号
let g:airline#extensions#tabline#buffer_nr_show = 1 

" These lines setup the environment to show graphics and colors correctly.



Plugin 'w0rp/ale'
Plugin 'vim-scripts/indentpython.vim'
Plugin 'Yggdroot/indentLine'
Plugin 'tmhedberg/SimpylFold'
let g:SimpylFold_docstring_preview=1

Plugin 'kien/ctrlp.vim'
Bundle 'davidhalter/jedi-vim'
Bundle 'ervandew/supertab'
Bundle 'scrooloose/nerdcommenter'
" nerdcommenter sets
" 让注释符与语句之间留一个空格
let g:NERDSpaceDelims=1

" 多行注释时样子更好看
let NERDCompactSexyComs=1
"将行注释符左对齐
let g:NERDDefaultAlign = 'left'
"加注释<leader>cc
"解开注释  <leader>cu   
"加上/解开注释, 智能判断<leader>c<space>  
"先复制, 再注解(p可以进行黏贴)<leader>cy   先复制, 再注解(p可以进行黏贴)


call vundle#end() " required

nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>
inoremap jj <Esc>
imap <C+s> <ESC>:w<CR>a

nnoremap <F6> :Autoformat<CR>
let g:autoformat_autoindent = 0
let g:autoformat_retab = 0
let g:autoformat_remove_trailing_spaces = 0

if !has("gui_running")                                          
    set t_Co=256                                                
endif                                                                                         
colorscheme khaki 

" jedi sets
let g:SuperTabDefaultCompletionType = "context"
let g:jedi#popup_on_dot = 0
let g:jedi#popup_select_first = 0
" All these mappings work only for python code:
" Go to definition
let g:jedi#goto_command = ',d'
" Find ocurrences
let g:jedi#usages_command = ',o'
" Find assignments
let g:jedi#goto_assignments_command = ',a'
" Go to definition in new tab
nmap ,D :tab split<CR>:call jedi#goto()<CR>

" Airline ------------------------------
let g:airline_powerline_fonts = 0
"let g:airline_theme = 'bubblegum'
let g:airline#extensions#whitespace#enabled = 0

" Color scheme
syntax enable
" let g:solarized_termcolors=16
" Allow powerline symbols to show up
let g:airline_powerline_fonts = 1

" NerdTree才插件的配置信息
" ""将F2设置为开关NERDTree的快捷键
map <f2> :NERDTreeToggle<cr>
" ""修改树的显示图标
let g:NERDTreeDirArrowExpandable = '+'
let g:NERDTreeDirArrowCollapsible = '-'
" ""窗口位置
let g:NERDTreeWinPos='left'
" ""窗口尺寸
let g:NERDTreeSize=30
" ""窗口是否显示行号
let g:NERDTreeShowLineNumbers=1
" ""不显示隐藏文件
let g:NERDTreeHidden=0
" rainbow_parentheses sets
let g:rbpt_colorpairs = [
                        \ ['brown',       'RoyalBlue3'],
                        \ ['Darkblue',    'SeaGreen3'],
                        \ ['darkgray',    'DarkOrchid3'],
                        \ ['darkgreen',   'firebrick3'],
                        \ ['darkcyan',    'RoyalBlue3'],
                        \ ['darkred',     'SeaGreen3'],
                        \ ['darkmagenta', 'DarkOrchid3'],
                        \ ['brown',       'firebrick3'],
                        \ ['gray',        'RoyalBlue3'],
                        \ ['darkmagenta', 'DarkOrchid3'],
                        \ ['Darkblue',    'firebrick3'],
                        \ ['darkgreen',   'RoyalBlue3'],
                        \ ['darkcyan',    'SeaGreen3'],
                        \ ['darkred',     'DarkOrchid3'],
                        \ ['red',         'firebrick3'],
                        \ ]
let g:rbpt_max = 16
let g:rbpt_loadcmd_toggle = 0
au VimEnter * RainbowParenthesesToggle
au Syntax * RainbowParenthesesLoadRound
au Syntax * RainbowParenthesesLoadSquare
au Syntax * RainbowParenthesesLoadBraces

" ale sets
let g:ale_fix_on_save = 1
let g:ale_completion_enabled = 1
let g:ale_sign_column_always = 1
let g:airline#extensions#ale#enabled = 1

"indentline sets
let g:indentLine_setColors = 0
let g:indentLine_color_term = 239


let python_highlight_all=1
au Filetype python set tabstop=4
au Filetype python set softtabstop=4
au Filetype python set shiftwidth=4
au Filetype python set textwidth=79
au Filetype python set expandtab
au Filetype python set autoindent
au Filetype python set fileformat=unix
autocmd Filetype python set foldmethod=indent
autocmd Filetype python set foldlevel=99

