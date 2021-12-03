Name:           openvswitch
Summary:        Production Quality, Multilayer Open Virtual Switch
URL:            http://www.openvswitch.org/
Version:        2.12.0
License:        ASL 2.0 and ISC
Release:        15
Source:         https://www.openvswitch.org/releases/openvswitch-%{version}.tar.gz
Buildroot:      /tmp/openvswitch-rpm
Patch0000:      0000-openvswitch-add-stack-protector-strong.patch
Patch0001:      0001-Remove-unsupported-permission-names.patch
Patch0002:      CVE-2020-35498-pre.patch
Patch0003:      CVE-2020-35498.patch
Patch0004:      CVE-2020-27827.patch
Patch0005:      CVE-2015-8011.patch
Patch0006:      backport-CVE-2021-36980.patch
Patch0007:      0002-fix-DPDK-compiling-error.patch
Patch0008:      0001-specifies-the-ovs-module-path.patch

Requires:       %{name}-help
Requires:       logrotate hostname python >= 2.7 python2-six selinux-policy-targeted libsepol >= 3.1
Requires:       openssl iproute module-init-tools
BuildRequires:  python2-six, openssl-devel checkpolicy selinux-policy-devel autoconf automake libtool python-sphinx unbound-devel
# required by python3-openvswitch and build configuration --with-dpdk --libcapng
BuildRequires:  python3-sphinx python3-devel python3-six libcap-ng-devel dpdk-devel libpcap-devel numactl-devel

Requires(pre): shadow-utils
Requires(post): /bin/sed
Requires(post): /usr/sbin/usermod
Requires(post): /usr/sbin/groupadd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Provides:       openvswitch-selinux-policy = %{version}-%{release}
Obsoletes:      openvswitch-selinux-policy < %{version}-%{release}
Obsoletes:      openvswitch-controller <= 0:2.1.0-1

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

%package -n python3-openvswitch
Summary: Open vSwitch python3 bindings
Requires: python3 python3-six
Obsoletes: python-openvswitch < 2.10.0-6
Provides: python-openvswitch = %{version}-%{release}

%description -n python3-openvswitch
Python bindings for the Open vSwitch database

%package test
Summary: Open vSwitch testing utilities
BuildArch: noarch
Requires: python3-openvswitch = %{version}-%{release}

%description test
Utilities that are useful to diagnose performance and connectivity issues in Open vSwitch setup.

%package -n network-scripts-%{name}
Summary: Open vSwitch legacy network service support
Requires: network-scripts
Supplements: (%{name} and network-scripts)

%description -n network-scripts-%{name}
This provides the ifup and ifdown scripts for use with the legacy network service.

%package ipsec
Summary: Open vSwitch IPsec tunneling support
Requires: openvswitch libreswan
Requires: python3-openvswitch = %{version}-%{release}

%description ipsec
This package provides IPsec tunneling support for OVS tunnels.

%package ovn-central
Summary: Open vSwitch - Open Virtual Network support
Requires: openvswitch openvswitch-ovn-common
Requires: firewalld-filesystem

%description ovn-central
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and
L3 overlays and security groups.

%package ovn-host
Summary: Open vSwitch - Open Virtual Network support
Requires: openvswitch openvswitch-ovn-common
Requires: firewalld-filesystem

%description ovn-host
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and
L3 overlays and security groups.

%package ovn-vtep
Summary: Open vSwitch - Open Virtual Network support
Requires: openvswitch openvswitch-ovn-common

%description ovn-vtep
OVN vtep controller

%package ovn-common
Summary: Open vSwitch - Open Virtual Network support
Requires: openvswitch

%description ovn-common
Utilities that are use to diagnose and manage the OVN components.

%prep
%autosetup -p1

%build
./boot.sh
autoreconf
./configure \
        --prefix=/usr \
        --sysconfdir=/etc \
        --localstatedir=%{_localstatedir} \
        --libdir=%{_libdir} \
        --enable-libcapng \
        --disable-static \
        --enable-ssl \
        --enable-shared \
        --with-dpdk \
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki 

/usr/bin/python3 build-aux/dpdkstrip.py \
        --dpdk \
        < rhel/usr_lib_systemd_system_ovs-vswitchd.service.in \
        > rhel/usr_lib_systemd_system_ovs-vswitchd.service

%make_build
make selinux-policy

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_rundir}/openvswitch
install -d -m 0750 $RPM_BUILD_ROOT%{_localstatedir}/log/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch

install -p -D -m 0644 \
        rhel/usr_share_openvswitch_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openvswitch
for service in openvswitch ovsdb-server ovs-vswitchd openvswitch-ipsec ovn-controller ovn-controller-vtep ovn-northd; do
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
install -m 0644 vswitchd/vswitch.ovsschema \
  $RPM_BUILD_ROOT/%{_datadir}/openvswitch/vswitch.ovsschema

install -p -m 644 -D selinux/openvswitch-custom.pp \
    $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}/openvswitch-custom.pp

pushd python
export CPPFLAGS="-I ../include"
export LDFLAGS="%{__global_ldflags} -L $RPM_BUILD_ROOT%{_libdir}"
%py3_build
%py3_install
[ -f "$RPM_BUILD_ROOT/%{python3_sitearch}/ovs/_json.cpython-%{python3_version_nodots}m-%{_arch}-%{_target_os}%{?_gnu}.so" ]
popd

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

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/openvswitch

touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/conf.db
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/.conf.db.~lock~
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/system-id.conf

install -d $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-central-firewall-service.xml \
  $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/ovn-central-firewall-service.xml
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-host-firewall-service.xml \
  $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/ovn-host-firewall-service.xml

install -d -m 0755 $RPM_BUILD_ROOT%{_prefix}/lib/ocf/resource.d/ovn
ln -s %{_datadir}/openvswitch/scripts/ovndb-servers.ocf \
  $RPM_BUILD_ROOT%{_prefix}/lib/ocf/resource.d/ovn/ovndb-servers

install -p -D -m 0755 \
        rhel/usr_share_openvswitch_scripts_ovs-systemd-reload \
        $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovs-systemd-reload

rm -rf $RPM_BUILD_ROOT/usr/include/openflow/
rm -rf $RPM_BUILD_ROOT/usr/include/ovn/
rm \
    $RPM_BUILD_ROOT/usr/bin/ovs-testcontroller \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-testcontroller.8 \
    $RPM_BUILD_ROOT/usr/bin/ovs-test \
    $RPM_BUILD_ROOT/usr/bin/ovs-l3ping \
    $RPM_BUILD_ROOT/usr/bin/ovn-docker-overlay-driver \
    $RPM_BUILD_ROOT/usr/bin/ovn-docker-underlay-driver \
    $RPM_BUILD_ROOT/usr/sbin/ovs-vlan-bug-workaround \
    $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovn-bugtool-nbctl-show \
    $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovn-bugtool-sbctl-lflow-list \
    $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovn-bugtool-sbctl-show
(cd "$RPM_BUILD_ROOT" && rm -rf usr/%{_lib}/*.la)

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%selinux_relabel_pre -s targeted
getent group openvswitch >/dev/null || groupadd -r openvswitch
getent passwd openvswitch >/dev/null || \
    useradd -r -g openvswitch -d / -s /sbin/nologin \
    -c "Open vSwitch Daemons" openvswitch
getent group hugetlbfs >/dev/null || groupadd hugetlbfs
usermod -a -G hugetlbfs openvswitch
exit 0

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

%preun ovn-central
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-northd.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-northd.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-northd.service >/dev/null 2>&1 || :
    fi
%endif

%preun ovn-host
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-controller.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-controller.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-controller.service >/dev/null 2>&1 || :
    fi
%endif

%preun ovn-vtep
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-controller-vtep.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-controller-vtep.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
%endif

%post
if [ $1 -eq 1 ]; then
    sed -i 's:^#OVS_USER_ID=:OVS_USER_ID=:' /etc/sysconfig/openvswitch
    sed -i \
        's@OVS_USER_ID="openvswitch:openvswitch"@OVS_USER_ID="openvswitch:hugetlbfs"@'\
        /etc/sysconfig/openvswitch
fi
chown -R openvswitch:openvswitch /etc/openvswitch

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

%post ovn-central
%if 0%{?systemd_post:1}
    %systemd_post ovn-northd.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post ovn-host
%if 0%{?systemd_post:1}
    %systemd_post ovn-controller.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post ovn-vtep
%if 0%{?systemd_post:1}
    %systemd_post ovn-controller-vtep.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%postun ovn-central
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-northd.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
    # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-northd.service >/dev/null 2>&1 || :
    fi
%endif

%postun ovn-host
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-controller.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-controller.service >/dev/null 2>&1 || :
    fi
%endif

%postun ovn-vtep
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-controller-vtep.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
%endif

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
%ghost %attr(0600,-,-) %verify(not owner group md5 size mtime) %{_sysconfdir}/openvswitch/.conf.db.~lock~
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
%{_libdir}/pkgconfig
%{_includedir}/openvswitch/*

%files help
/usr/share/man/man1/*
/usr/share/man/man5/*
/usr/share/man/man7/*
/usr/share/man/man8/*
%doc README.rst NEWS rhel/README.RHEL.rst

%files -n python3-openvswitch
%{python3_sitearch}/ovs
%{python3_sitearch}/ovs-*.egg-info
%doc LICENSE

%files test
%{_bindir}/ovs-pcap
%{_bindir}/ovs-tcpdump
%{_bindir}/ovs-tcpundump
%{_mandir}/man1/ovs-pcap.1*
%{_mandir}/man8/ovs-tcpdump.8*
%{_mandir}/man1/ovs-tcpundump.1*
%exclude %{_mandir}/man8/ovs-test.8*
%exclude %{_mandir}/man8/ovs-vlan-test.8*
%exclude %{_mandir}/man8/ovs-l3ping.8*

%files -n network-scripts-%{name}
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs

%files ipsec
%{_datadir}/openvswitch/scripts/ovs-monitor-ipsec
%{_unitdir}/openvswitch-ipsec.service

%files ovn-common
%{_bindir}/ovn-detrace
%{_bindir}/ovn-nbctl
%{_bindir}/ovn-sbctl
%{_bindir}/ovn-trace
%{_datadir}/openvswitch/scripts/ovn-ctl
%{_datadir}/openvswitch/scripts/ovndb-servers.ocf
%{_mandir}/man1/ovn-detrace.1*
%{_mandir}/man8/ovn-ctl.8*
%{_mandir}/man8/ovn-nbctl.8*
%{_mandir}/man8/ovn-trace.8*
%{_mandir}/man7/ovn-architecture.7*
%{_mandir}/man8/ovn-sbctl.8*
%{_mandir}/man5/ovn-nb.5*
%{_mandir}/man5/ovn-sb.5*
%{_prefix}/lib/ocf/resource.d/ovn/ovndb-servers

%files ovn-central
%{_bindir}/ovn-northd
%{_mandir}/man8/ovn-northd.8*
%config %{_datadir}/openvswitch/ovn-nb.ovsschema
%config %{_datadir}/openvswitch/ovn-sb.ovsschema
%{_unitdir}/ovn-northd.service
%{_prefix}/lib/firewalld/services/ovn-central-firewall-service.xml

%files ovn-host
%{_bindir}/ovn-controller
%{_mandir}/man8/ovn-controller.8*
%{_unitdir}/ovn-controller.service
%{_prefix}/lib/firewalld/services/ovn-host-firewall-service.xml

%files ovn-vtep
%{_bindir}/ovn-controller-vtep
%{_mandir}/man8/ovn-controller-vtep.8*
%{_unitdir}/ovn-controller-vtep.service

%changelog
* Thu Dec 02 2021 wulei <wulei80@huawei.com> - 2.12.0-15
- Rectify the failure to start openvswitch-ipesc and ovn-controller-vtep services

* Thu Oct 18 2021 yangcheng <yangcheng87@huawei.com> - 2.12.0-14
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
