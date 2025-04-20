$hosts =,"iqn.1991-05.com.microsoft:hc380-bench-01"
$hosts+=,"iqn.1991-05.com.microsoft:hc380-bench-02"
$hosts+=,"iqn.1991-05.com.microsoft:hc380-bench-03"
$hosts+=,"iqn.1991-05.com.microsoft:hc380-bench-04"
$volumes=4
$replication=2
$size=90
$login="login=192.168.58.142 username=powershell password=HPFuture16!"
$cluster="HPE-HC380-Storage"
$ao=1
$thin=1

for($i=1;  $i -le $volumes; $i++)
{
Invoke-Expression ('cliq deletevolume volumename=Volume{0} {1} prompt=false' -f $i, $login)
}