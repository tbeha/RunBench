$hosts =,"iqn.1993-08.org.debian:01:sdsdl361.vdi.local"
$hosts+=,"iqn.1993-08.org.debian:01:sdsdl362.vdi.local"
$hosts+=,"iqn.1993-08.org.debian:01:sdsdl363.vdi.local"
$volumes=18
$replication=2
$size=800
$login="login=192.168.55.39 username=powershell password=HPFuture15!"
$cluster="svbenchcl"
$ao=0
$thin=1

for($i=7; $i -le $volumes; $i++)
{
Invoke-Expression ('cliq.exe createvolume volumename=Volume{0} clustername={1} size={2}GB replication={3} adaptiveoptimization={4} thinprovision={5} {6}' -f $i, $cluster, $size, $replication, $ao, $thin, $login)
Invoke-Expression ('cliq.exe assignvolume volumename=Volume{0} initiator={1} {2}' -f $i, $hosts[$($i%3)], $login)
}