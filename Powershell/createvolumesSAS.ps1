$hosts =,"iqn.1991-05.com.microsoft:hc380-bench-01"
$hosts+=,"iqn.1991-05.com.microsoft:hc380-bench-02"
$hosts+=,"iqn.1991-05.com.microsoft:hc380-bench-03"
$hosts+=,"iqn.1991-05.com.microsoft:hc380-bench-04"
$login="login=192.168.58.142 username=powershell password=HPFuture16!"
$cluster="HPE-HC380-Storage"
$volumes=12
$replication=2
$size=375
$ao=0
$thin=1

for($i=5; $i -le $volumes; $i++)
{
Invoke-Expression ('cliq.exe createvolume volumename=Volume{0} clustername={1} size={2}GB replication={3} adaptiveoptimization={4} thinprovision={5} {6}' -f $i, $cluster, $size, $replication, $ao, $thin, $login)
Invoke-Expression ('cliq.exe assignvolume volumename=Volume{0} initiator={1} {2}' -f $i, $hosts[$($i%4)], $login)
}