#!/usr/bin/awk -f

BEGIN {
	# 设置分隔符和输出连接符
	FS=":"
	OFS=":"
	# 初始化变量
	accounts=0
}
{
	$2=""
	print $0
	accounts++
}
END {
	print accounts " accounts.\n"
}
