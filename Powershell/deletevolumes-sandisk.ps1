$hosts =,"iqn.1991-05.com.microsoft:svbenchvm-1.vdi.local"
$hosts+=,"iqn.1991-05.com.microsoft:svbenchvm-2.vdi.local"
$hosts+=,"iqn.1991-05.com.microsoft:svbenchvm-3.vdi.local"
$volumes=18
$replication=2
$size=300
$login="login=192.168.55.63 username=powershell password=HPFuture15!"
$cluster="sandiskcl"
$ao=1
$thin=1

for($i=1;  $i -le $volumes; $i++)
{
Invoke-Expression ('cliq deletevolume volumename=Volume{0} {1} prompt=false' -f $i, $login)
}