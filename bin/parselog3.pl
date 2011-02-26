#!/usr/bin/perl
use strict;
use warnings;

use Term::ANSIColor;
use Text::Reform;
use utf8;

my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
my $now = sprintf "%04d-%02d-%02d", ($year+1900, $mon+1, $mday);

binmode STDOUT, ':utf8';

my $username = '';
my $date = '';
my $message = '';

my $format = "| [[[[[[[[[[[[[[[[[[[[[[[ | ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]] | [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[ |";
my %h_id2username = ();
my %h_records = ();

while (<>) {
    binmode ARGV, ':utf8';
    if (/WARNING username/) {
        chomp;
        my @a = split('WARNING', $_);
        $a[1] =~ s/.* = //;
        $username = $a[1];
        $date = $a[0];
    } elsif (/WARNING (\d{6}):\tusername/) {
        my $id = $1;
        chomp;
        my @a = split('WARNING', $_);
        $a[1] =~ s/.* = //;
        $username = $a[1];
        $date = $a[0];
        $h_id2username{$id} = [$username, $date];
    } elsif (/(INFO|WARNING) download/) {
        chomp;
        s/.*(INFO|WARNING)//;
        my $num = 0;
        my $size = 0;
        if (/ download (\d+) file for (\d+) octets/) {
            $num = $1;
            $size = $2;
        }
        if ($username ne '' and !/ 0 /) {
            my @a_date = split(' ', $date);
            if (! defined $h_records{$username}) { $h_records{$username} = {}; }
            if (! defined $h_records{$username}{$a_date[0]}) { $h_records{$username}{$a_date[0]} = []; }
            push(@{$h_records{$username}{$a_date[0]}}, [$date, $username, $num, $size]);
        }
    } elsif (/(INFO|WARNING) (\d{6}):\tdownload/) {
        my $id = $2;
        chomp;
        s/.*(INFO|WARNING) (\d{6}):\t//;
        if (defined $h_id2username{$id} and !/ 0 /) {
            my $num = 0;
            my $size = 0;
            if ($_ =~ /download (\d+) file for (\d+) octets/) {
                $num = $1;
                $size = $2;
            }

            my @a_date = split(' ', $h_id2username{$id}[1]);
            my $username = $h_id2username{$id}[0];
            if (! defined $h_records{$username}) { $h_records{$username} = {}; }
            if (! defined $h_records{$username}{$a_date[0]}) { $h_records{$username}{$a_date[0]} = []; }
            push(@{$h_records{$username}{$a_date[0]}}, [$h_id2username{$id}[1], $h_id2username{$id}[0], $num, $size]);
        }
    }
}

use Data::Dumper;

foreach $username (sort keys %h_records) {
    my $today;
    my $t_num = 0;
    my $t_size = 0;

    foreach $date (sort keys %{$h_records{$username}}) {
        if ($date eq $now) {
            $today = $h_records{$username}{$date};
        } else {
            my $daily = '';
            foreach $daily (@{$h_records{$username}{$date}}) {
                $t_num = $t_num + $daily->[2];
                $t_size = $t_size + $daily->[3];
            }
        }
    }
    if ($t_num < 10) {
        print color "green";
    } elsif ($t_num < 50) {
        print color "yellow";
    } else {
        print color "red";
    }
    print form $format, " < $now", $username, sprintf "download %d file for %d octets", ($t_num, $t_size);
    print color 'reset';
    my $line = '';
    if (defined $today) {
        print color "blue";
        foreach $line (@$today) {
            if ($line->[2] > 5) {
                print color "bold";
            }
            print form $format, $line->[0], $line->[1], sprintf "download %d file for %d octets", ($line->[2], $line->[3]);
        }
        print color "reset";
    }
}

#            print form $format, $date, $username, $_;
