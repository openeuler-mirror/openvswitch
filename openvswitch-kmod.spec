# Spec file for Open vSwitch kernel modules on openEuler version.

# Copyright (C) 2011, 2012, 2018 Nicira, Inc.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.

#needsrootforbuild

%define kversion        $(uname -r)
%{?kversion:%define kernel %kversion}

Name: openvswitch-kmod
Version: 2.12.0
Release: 1
Summary: Open vSwitch Kernel Modules
License: GPLv2
URL: http://www.openvswitch.org/
Source: openvswitch-%{version}.tar.gz

#Source1: openvswitch-init
Buildroot: /tmp/openvswitch-xen-rpm
Provides: kmod-openvswitch
Conflicts: kmod-openvswitch

BuildRequires: python-six
BuildRequires: openssl-devel
BuildRequires: checkpolicy, selinux-policy-devel
BuildRequires: autoconf, automake, libtool
BuildRequires: python-sphinx
BuildRequires:  kernel kernel-devel
%undefine _enable_debug_packages
%description
Open vSwitch Linux kernel module

%prep
%setup -q -n openvswitch-%{version}

%build
sh boot.sh
for kv in %{kversion}; do
    mkdir -p _$kv
    (cd _$kv && /bin/cp -f ../configure . && %configure --srcdir=.. \
        --with-linux=/lib/modules/${kv}/build --enable-ssl %{_ovs_config_extra_flags})
    make %{_smp_mflags} -C _$kv/datapath/linux
done

%install
export INSTALL_MOD_DIR=extra/openvswitch
rm -rf $RPM_BUILD_ROOT
for kv in %{kversion}; do
    make INSTALL_MOD_PATH=$RPM_BUILD_ROOT -C _$kv/datapath/linux modules_install
done
mkdir -p $RPM_BUILD_ROOT/etc/depmod.d
for kv in %{kversion}; do
    for module in $RPM_BUILD_ROOT/lib/modules/${kv}/extra/openvswitch/*.ko
    do
        modname="$(basename ${module})"
        grep -qsPo "^\s*override ${modname%.ko} \* extra\/openvwitch" \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf || \
            echo "override ${modname%.ko} * extra/openvswitch" >> \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf
        grep -qsPo "^\s*override ${modname%.ko} \* weak-updates\/openvwitch" \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf || \
            echo "override ${modname%.ko} * weak-updates/openvswitch" >> \
            $RPM_BUILD_ROOT/etc/depmod.d/kmod-openvswitch.conf
    done
done
install -d -m 0755 $RPM_BUILD_ROOT/usr/share/openvswitch/scripts
install -p -m 0755 rhel/usr_share_openvswitch_scripts_ovs-kmod-manage.sh \
    $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovs-kmod-manage.sh

%clean
rm -rf $RPM_BUILD_ROOT

%post
current_kernel=$(uname -r)
IFS=. read installed_major installed_minor installed_micro installed_arch \
    installed_build <<<"${current_kernel##*-}"
if [ "$installed_major" = "327" ] || [ "$installed_major" = "693" ]; then
    # Workaround for RHEL 7.2 and 7.4
    if [ -x "/usr/share/%{oname}/scripts/ovs-kmod-manage.sh" ]; then
        /usr/share/%{oname}/scripts/ovs-kmod-manage.sh
    fi
else
    # Ensure that modprobe will find our modules.
    for k in $(cd /lib/modules && /bin/ls); do
        [ -d "/lib/modules/$k/kernel/" ] && /sbin/depmod -a "$k"
    done
    if [ -x "/sbin/weak-modules" ]; then
        rpm -ql kmod-%{oname} | grep '\.ko$' | \
            /sbin/weak-modules --add-modules
    fi
fi

%postun
if [ "$1" = 0 ]; then  # Erase, not upgrade
    for kname in `ls -d /lib/modules/*`
do
    rm -rf $kname/weak-updates/openvswitch
done
fi
/sbin/depmod -a

%files
%defattr(0644,root,root)
/lib/modules/
/etc/depmod.d/kmod-openvswitch.conf
%attr(755,root,root) /usr/share/openvswitch/scripts/ovs-kmod-manage.sh

%changelog
* Fri Nov 22 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.12.0
- First build 
