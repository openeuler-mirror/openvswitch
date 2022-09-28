Name:           openvswitch
Summary:        Production Quality, Multilayer Open Virtual Switch
URL:            http://www.openvswitch.org/
Version:        2.12.4
License:        ASL 2.0 and ISC
Release:        1
Source:         https://www.openvswitch.org/releases/openvswitch-%{version}.tar.gz
Buildroot:      /tmp/openvswitch-rpm
Patch0000:      0000-openvswitch-add-stack-protector-strong.patch
Patch0001:      0001-Remove-unsupported-permission-names.patch

Requires:       %{name}-help
Requires:       logrotate hostname python >= 2.7 python2-six selinux-policy-targeted libsepol >= 3.1
BuildRequires:  python2-six, openssl-devel checkpolicy selinux-policy-devel autoconf automake libtool python-sphinx unbound-devel
Provides:       openvswitch-selinux-policy = %{version}-%{release}
Obsoletes:      openvswitch-selinux-policy < %{version}-%{release}

%bcond_without check
%bcond_with check_datapath_kernel

%description
Open vSwitch is a production quality, multilayer virtual switch licensed under
the open source Apache 2.0 license.

%package devel
Summary:        Development tools for Open vSwitch

%description devel
Libraries, header files, and other development tools for Open vSwitch.

%package help
Summary:        Helpful information for Open vSwitch

%description help
Documents and helpful information for Open vSwitch.

%prep
%autosetup -p1

%build
autoreconf
./configure \
        --prefix=/usr \
        --sysconfdir=/etc \
        --localstatedir=%{_localstatedir} \
        --libdir=%{_libdir} \
        --enable-ssl \
        --enable-shared \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki \
        PYTHON=%{__python2}

build-aux/dpdkstrip.py \
        --nodpdk \
        < rhel/usr_lib_systemd_system_ovs-vswitchd.service.in \
        > rhel/usr_lib_systemd_system_ovs-vswitchd.service

%make_build
make selinux-policy

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch

install -p -D -m 0644 \
        rhel/usr_share_openvswitch_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openvswitch
for service in openvswitch ovsdb-server ovs-vswitchd; do
        install -p -D -m 0644 \
                        rhel/usr_lib_systemd_system_${service}.service \
                        $RPM_BUILD_ROOT%{_unitdir}/${service}.service
done

install -m 0755 rhel/etc_init.d_openvswitch                              $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/openvswitch.init
install -D -m 0644 rhel/etc_logrotate.d_openvswitch                      $RPM_BUILD_ROOT/etc/logrotate.d/openvswitch
install -D -m 0644 rhel/etc_openvswitch_default.conf                     $RPM_BUILD_ROOT/%{_sysconfdir}/openvswitch/default.conf
install -D -m 0755 rhel/etc_sysconfig_network-scripts_ifup-ovs           $RPM_BUILD_ROOT/etc/sysconfig/network-scripts/ifup-ovs
install -D -m 0755 rhel/etc_sysconfig_network-scripts_ifdown-ovs         $RPM_BUILD_ROOT/etc/sysconfig/network-scripts/ifdown-ovs
install -D -m 0644 rhel/usr_share_openvswitch_scripts_sysconfig.template $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/sysconfig.template

install -p -m 644 -D selinux/openvswitch-custom.pp \
    $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}/openvswitch-custom.pp

rm \
    $RPM_BUILD_ROOT/usr/bin/ovs-testcontroller \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-testcontroller.8 \
    $RPM_BUILD_ROOT/usr/bin/ovs-test \
    $RPM_BUILD_ROOT/usr/bin/ovs-l3ping \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-test.8 \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-l3ping.8 \
    $RPM_BUILD_ROOT/usr/sbin/ovs-vlan-bug-workaround \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-vlan-bug-workaround.8 \
    $RPM_BUILD_ROOT/usr/bin/ovn-* \
    $RPM_BUILD_ROOT/usr/share/man/man?/ovn-* \
    $RPM_BUILD_ROOT/usr/share/openvswitch/ovn-* \
    $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovn*
(cd "$RPM_BUILD_ROOT" && rm -rf usr/%{_lib}/*.la)
(cd "$RPM_BUILD_ROOT" && rm -rf usr/include)

install -d -m 0755 $RPM_BUILD_ROOT%{_rundir}/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT%{_localstatedir}/log/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT/var/lib/openvswitch

install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/openflow
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse/arpa
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse/netinet
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse/sys
install -d -m 0755 $RPM_BUILD_ROOT/%{_includedir}/openvswitch/lib
install -m 0644 include/*.h                $RPM_BUILD_ROOT/%{_includedir}/openvswitch
install -m 0644 include/openflow/*.h       $RPM_BUILD_ROOT/%{_includedir}/openvswitch/openflow
install -m 0644 include/openvswitch/*.h    $RPM_BUILD_ROOT/%{_includedir}/openvswitch/openvswitch
install -m 0644 include/sparse/*.h         $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse
install -m 0644 include/sparse/arpa/*.h    $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse/arpa
install -m 0644 include/sparse/netinet/*.h $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse/netinet
install -m 0644 include/sparse/sys/*.h     $RPM_BUILD_ROOT/%{_includedir}/openvswitch/sparse/sys
install -m 0644 lib/*.h                    $RPM_BUILD_ROOT/%{_includedir}/openvswitch/lib

install -D -m 0644 lib/.libs/libopenvswitch.a \
    $RPM_BUILD_ROOT/%{_libdir}/libopenvswitch.a

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/openvswitch

touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/conf.db
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/.conf.db.~lock~
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/system-id.conf

install -d $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/

install -p -D -m 0755 \
        rhel/usr_share_openvswitch_scripts_ovs-systemd-reload \
        $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovs-systemd-reload

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%selinux_relabel_pre -s targeted

%preun
%if 0%{?systemd_preun:1}
    %systemd_preun %{name}.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
        /bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
    fi
%endif

%post
%if 0%{?systemd_post:1}
    # This may not enable openvswitch service or do daemon-reload.
    %systemd_post %{name}.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%selinux_modules_install -s targeted /usr/share/selinux/packages/%{name}/openvswitch-custom.pp

%postun
%if 0%{?systemd_postun:1}
    %systemd_postun %{name}.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

if [ $1 -eq 0 ] ; then
  %selinux_modules_uninstall -s targeted openvswitch-custom
fi
exit 0

%posttrans
%selinux_relabel_post -s targeted

%files
%defattr(-,root,root)
%dir /etc/openvswitch
/etc/bash_completion.d/ovs-appctl-bashcomp.bash
/etc/bash_completion.d/ovs-vsctl-bashcomp.bash
%config(noreplace) /etc/logrotate.d/openvswitch
/etc/sysconfig/network-scripts/ifup-ovs
/etc/sysconfig/network-scripts/ifdown-ovs
/usr/bin/ovs-appctl
/usr/bin/ovs-dpctl
/usr/bin/ovs-dpctl-top
/usr/bin/ovs-docker
/usr/bin/ovs-ofctl
/usr/bin/ovs-parse-backtrace
/usr/bin/ovs-pcap
/usr/bin/ovs-pki
/usr/bin/ovs-tcpdump
/usr/bin/ovs-tcpundump
/usr/bin/ovs-vlan-test
/usr/bin/ovs-vsctl
/usr/bin/ovsdb-client
/usr/bin/ovsdb-tool
/usr/bin/vtep-ctl
%{_libdir}/lib*.so.*
/usr/sbin/ovs-bugtool
/usr/sbin/ovs-vswitchd
/usr/sbin/ovsdb-server
/usr/share/openvswitch/bugtool-plugins/
/usr/share/openvswitch/python/
/usr/share/openvswitch/scripts/ovs-bugtool-*
/usr/share/openvswitch/scripts/ovs-check-dead-ifs
/usr/share/openvswitch/scripts/ovs-ctl
/usr/share/openvswitch/scripts/ovs-kmod-ctl
/usr/share/openvswitch/scripts/ovs-lib
/usr/share/openvswitch/scripts/ovs-save
/usr/share/openvswitch/scripts/ovs-vtep
/usr/share/openvswitch/scripts/sysconfig.template
/usr/share/openvswitch/scripts/ovs-monitor-ipsec
%{_sysconfdir}/openvswitch/default.conf
%config %ghost %{_sysconfdir}/openvswitch/conf.db
%ghost %{_sysconfdir}/openvswitch/.conf.db.~lock~
%config %ghost %{_sysconfdir}/openvswitch/system-id.conf
%config(noreplace) %{_sysconfdir}/sysconfig/openvswitch
%defattr(-,root,root)
%{_unitdir}/openvswitch.service
%{_unitdir}/ovsdb-server.service
%{_unitdir}/ovs-vswitchd.service
/usr/share/openvswitch/scripts/openvswitch.init
/usr/share/openvswitch/scripts/ovs-systemd-reload
/usr/share/openvswitch/vswitch.ovsschema
/usr/share/openvswitch/vtep.ovsschema
%doc NOTICE
/var/lib/openvswitch
/var/log/openvswitch
%{_datadir}/selinux/packages/%{name}/openvswitch-custom.pp

%files devel
%{_libdir}/lib*.so
%{_libdir}/lib*.a
%{_libdir}/pkgconfig
%{_includedir}/openvswitch/*

%files help
/usr/share/man/man1/*
/usr/share/man/man5/*
/usr/share/man/man7/*
/usr/share/man/man8/*
%doc README.rst NEWS rhel/README.RHEL.rst

%changelog
* Wed Sep 28 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.4-1
- upgrade to 2.12.4

* Mon Jul 25 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.0-16
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:revent "Add host, ipsec and ovn subpackage"

* Wed Jul 13 2022 zhouwenpei <zhouwenpei1@h-pattners.com> - 2.12.0-15
- Type:cve
- ID:CVE-2021-3905
- SUG:NA
- DESC:fix CVE-2021-3905

* Tue Nov 2 2021 yangcheng <yangcheng87@huawei.com> - 2.12.0-14
- Type:bugfix
- ID:NA
- SUG:NA
- DESC: fix the error of opevswitch installation and upgrade

* Fri Aug 27 2021 Ge Wang <wangge20@openeuler.org> - 2.12.0-13
- Add host, ipsec and ovn subpackage

* Thu Jul 29 2021 liuyumeng <liuyumeng5@huawei.com> - 2.12.0-12
- Type:cve
- ID:CVE-2021-36980 
- SUG:NA
- DESC: fix CVE-2021-36980

* Mon Apr 12 2021 liuyiguo <liuyiguo1@huawei.com> - 2.12.0-11
- Change the OVS startup mode to service startup.

* Wed Mar 31 2021 wangyue <wangyue92@huawei.com> - 2.12.0-10
- fix CVE-2020-27827 CVE-2015-8011

* Mon Mar 01 2021 wangyue <wangyue92@huawei.com> - 2.12.0-9
- fix CVE-2020-35498

* Wed Nov 18 2020 maminjie <maminjie1@huawei.com> - 2.12.0-8
- Remove unsupported permission names

* Fri Nov 06 2020 caodongxia <caodongxia@huawei.com> - 2.12.0-7
- Add install requires help package into main package

* Fri Sep 25 2020 luosuwang <oenetdev@huawei.com> - 2.12.0-6
- Remove openvswitch-kmod package

* Wed Mar 18 2020 zhangtao <zhangtao221@huawei.com> - 2.12.0-5
- add stack protector

* Tue Mar 17 2020 gulining <gulining1@huawei.com> - 2.12.0-4
- remove extra spaces to resolve compile error

* Mon Mar 16 2020 jiangkai <jiangkai20@huawei.com> - 2.12.0-3
- Package init
