$hosts =,"iqn.1991-05.com.microsoft:svbenchvm-1.vdi.local"
$hosts+=,"iqn.1991-05.com.microsoft:svbenchvm-2.vdi.local"
$hosts+=,"iqn.1991-05.com.microsoft:svbenchvm-3.vdi.local"
$volumes=25
$replication=2
$size=300
$login="login=192.168.58.62 username=powershell password=HPFuture15!"
$cluster="sandiskcl"
$ao=1
$thin=1

for($i=20; $i -le $volumes; $i++)
{
Invoke-Expression ('cliq createvolume volumename=Volume{0} clustername={1} size={2}GB replication={3} adaptiveoptimization={4} thinprovision={5} {6}' -f $i, $cluster, $size, $replication, $ao, $thin, $login)
Invoke-Expression ('cliq assignvolume volumename=Volume{0} initiator={1} {2}' -f $i, $hosts[$($i%3)], $login)
}