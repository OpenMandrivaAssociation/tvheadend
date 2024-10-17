# import from MIB and upadte to 3.9

Name:           tvheadend
Summary:        TV streaming server
Version:        3.9
Release:        3
License:        GPLv3
URL:            https://www.lonelycoder.com
Group:          Video
Source0:        https://github.com/tvheadend/tvheadend/archive/v3.9.tar.gz
Source1:        %{name}.service
Source2:        %{name}.png
Source3:        README.install.urpmi
Source4:        %{name}.conf


Patch0: 	    %{name}-no_werror.patch
BuildRequires:  fdupes
BuildRequires:	pkgconfig
BuildRequires:  pkgconfig(avahi-client)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(python)
BuildRequires:  systemd
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libv4lconvert)

Requires(pre,preun):  rpm-helper
Requires(post):       pwgen

%description
A TV streaming server supporting DVB-S, DVB-S2, DVB-C, DVB-T, ATSC, IPTV,
and Analog video (V4L) as input sources.

It also comes with a powerful and easy to use web interface both used for
configuration and day-to-day operations, such as searching the EPG and
scheduling recordings.


%prep
%setup -q
%patch0 -p1
cp -v %{SOURCE3} .

%build
%configure --prefix=/usr --release --libdir=%{_libdir} --mandir=%{_mandir}/man1 --disable-dvbscan
%make


%install
%makeinstall_std
mkdir -p %{buildroot}/%{_localstatedir}/lib/%{name}/.hts/%{name}/accesscontrol
cp -v %{SOURCE4} %{buildroot}/%{_localstatedir}/lib/%{name}/.hts/%{name}/accesscontrol/1

mkdir -p %{buildroot}/%{_unitdir}
install -m0644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service

# Menu entry
mkdir -p %{buildroot}/%{_datadir}/applications
cat > %{buildroot}/%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Name=Tvheadend
Comment=%{summary}
Exec=%{_bindir}/xdg-open http://localhost:9981/
Icon=%{name}
Type=Application
Categories=AudioVideo;Video;TV;Recorder;X-Mandriva-CrossDesktop;
EOF

install -D -m 644 %{SOURCE2} %{buildroot}/%{_iconsdir}/%{name}.png

find %{buildroot} -size 0 -delete

install -m644 %{SOURCE3} README.urpmi

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /sbin/nologin
gpasswd -a %{name} video >/dev/null

%post
chown %{name}:root %{_localstatedir}/lib/%{name} 
cd %{_localstatedir}/lib/%{name}
chown -R %{name}:video .hts*

if  grep -q '"password": "dummypassword"' %{_localstatedir}/lib/%{name}/.hts/%{name}/accesscontrol/1; then
  sed -i "s,\"password\": \"dummypassword\",\"password\": \"$(pwgen -s 12 1)\"," %{_localstatedir}/lib/%{name}/.hts/%{name}/accesscontrol/1
fi

%systemd_post %{name}

%preun
%systemd_preun %{name}


%files

%doc LICENSE README README.urpmi
%{_bindir}/%{name}
%attr(0644,root,root) %{_unitdir}/%{name}.service
%{_mandir}/man1/%{name}.1.xz
%{_iconsdir}/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/%{name}

%dir %attr(-,tvheadend,root) %{_localstatedir}/lib/%{name}
%dir %attr(-,tvheadend,video) %{_localstatedir}/lib/%{name}/.hts/%{name}/accesscontrol
%attr(0600,tvheadend,video) %{_localstatedir}/lib/%{name}/.hts/%{name}/accesscontrol/1
